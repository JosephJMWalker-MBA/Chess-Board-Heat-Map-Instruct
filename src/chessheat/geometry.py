import chess
from pydantic import BaseModel, Field
from typing import List, Tuple, Optional, Set, FrozenSet

class PieceRef(BaseModel):
    square: str
    symbol: str

    model_config = {"frozen": True}

class AttackRelationship(BaseModel):
    attacker: PieceRef
    target_square: str
    target_piece: Optional[PieceRef] = None
    is_defense: bool = False

    model_config = {"frozen": True}

class SlidingRay(BaseModel):
    source: PieceRef
    direction_name: str
    path: Tuple[str, ...]
    target_square: str
    target_piece: Optional[PieceRef] = None

    model_config = {"frozen": True}

class PieceMobility(BaseModel):
    piece: PieceRef
    pseudo_legal_destinations: Tuple[str, ...]
    legal_destinations: Tuple[str, ...]

    model_config = {"frozen": True}

class BoardGeometry(BaseModel):
    fen: str
    attacks: FrozenSet[AttackRelationship]
    defenses: FrozenSet[AttackRelationship]
    rays: FrozenSet[SlidingRay]
    mobility: FrozenSet[PieceMobility]

class GeometryDelta(BaseModel):
    appeared_attacks: List[AttackRelationship]
    disappeared_attacks: List[AttackRelationship]
    appeared_defenses: List[AttackRelationship]
    disappeared_defenses: List[AttackRelationship]
    appeared_rays: List[SlidingRay]
    disappeared_rays: List[SlidingRay]
    mobility_gained: List[Tuple[PieceRef, str]] # (piece, square)
    mobility_lost: List[Tuple[PieceRef, str]]

def _get_piece_ref(board: chess.Board, sq: chess.Square) -> Optional[PieceRef]:
    p = board.piece_at(sq)
    if p:
        return PieceRef(square=chess.square_name(sq), symbol=p.symbol())
    return None

def extract_geometry(board: chess.Board) -> BoardGeometry:
    attacks = set()
    defenses = set()
    rays = set()
    mobility_list = set()

    legal_moves = list(board.generate_legal_moves())
    pseudo_legal_moves = list(board.generate_pseudo_legal_moves())

    for sq in chess.SQUARES:
        piece = board.piece_at(sq)
        if not piece:
            continue

        pref = PieceRef(square=chess.square_name(sq), symbol=piece.symbol())

        # Mobility
        p_legal = tuple(sorted([chess.square_name(m.to_square) for m in pseudo_legal_moves if m.from_square == sq]))
        l_legal = tuple(sorted([chess.square_name(m.to_square) for m in legal_moves if m.from_square == sq]))
        mobility_list.add(PieceMobility(piece=pref, pseudo_legal_destinations=p_legal, legal_destinations=l_legal))

        # Attacks & Defenses
        attacked_squares = board.attacks(sq)
        for target_sq in attacked_squares:
            target_piece = board.piece_at(target_sq)
            tref = _get_piece_ref(board, target_sq)

            is_defense = False
            if target_piece and target_piece.color == piece.color:
                is_defense = True

            rel = AttackRelationship(
                attacker=pref,
                target_square=chess.square_name(target_sq),
                target_piece=tref,
                is_defense=is_defense
            )

            if is_defense:
                defenses.add(rel)
            else:
                attacks.add(rel)

        # Rays
        if piece.piece_type in (chess.ROOK, chess.BISHOP, chess.QUEEN):
            directions = []
            if piece.piece_type in (chess.ROOK, chess.QUEEN):
                directions.extend([
                    ("N", 8), ("S", -8), ("E", 1), ("W", -1)
                ])
            if piece.piece_type in (chess.BISHOP, chess.QUEEN):
                directions.extend([
                    ("NE", 9), ("NW", 7), ("SE", -7), ("SW", -9)
                ])

            for dir_name, step in directions:
                current_sq = sq
                path = []
                target_sq = None
                target_p = None

                while True:
                    # check edge wrap
                    if step == 1 and chess.square_file(current_sq) == 7: break
                    if step == -1 and chess.square_file(current_sq) == 0: break
                    if step in (7, 9, -7, -9):
                        # diagonal edge checks
                        cf = chess.square_file(current_sq)
                        if (step == 9 or step == -7) and cf == 7: break
                        if (step == 7 or step == -9) and cf == 0: break

                    next_sq = current_sq + step
                    if not (0 <= next_sq <= 63):
                        break

                    p = board.piece_at(next_sq)
                    if p:
                        target_sq = next_sq
                        target_p = p
                        break
                    else:
                        path.append(next_sq)
                        target_sq = next_sq
                        current_sq = next_sq

                if target_sq is not None:
                    rays.add(SlidingRay(
                        source=pref,
                        direction_name=dir_name,
                        path=tuple(chess.square_name(s) for s in path),
                        target_square=chess.square_name(target_sq),
                        target_piece=_get_piece_ref(board, target_sq)
                    ))

    return BoardGeometry(
        fen=board.fen(),
        attacks=frozenset(attacks),
        defenses=frozenset(defenses),
        rays=frozenset(rays),
        mobility=frozenset(mobility_list)
    )

def compute_geometry_delta(before: BoardGeometry, after: BoardGeometry) -> GeometryDelta:
    app_attacks = sorted(list(after.attacks - before.attacks), key=lambda x: (x.attacker.square, x.target_square))
    dis_attacks = sorted(list(before.attacks - after.attacks), key=lambda x: (x.attacker.square, x.target_square))

    app_defenses = sorted(list(after.defenses - before.defenses), key=lambda x: (x.attacker.square, x.target_square))
    dis_defenses = sorted(list(before.defenses - after.defenses), key=lambda x: (x.attacker.square, x.target_square))

    app_rays = sorted(list(after.rays - before.rays), key=lambda x: (x.source.square, x.direction_name))
    dis_rays = sorted(list(before.rays - after.rays), key=lambda x: (x.source.square, x.direction_name))

    # Mobility delta
    # Pieces might move, so their 'square' changes. But for absolute pins, we usually care about the pinned piece staying put.
    # To track mobility gained/lost per piece properly, we should match by PieceRef.
    # If a piece moves, its PieceRef changes, so we will see a lot of "lost all mobility on e2" and "gained on e4".
    # This is factually correct.
    before_mob = {m.piece: m for m in before.mobility}
    after_mob = {m.piece: m for m in after.mobility}

    mob_gained = []
    mob_lost = []

    all_pieces = set(before_mob.keys()) | set(after_mob.keys())
    for pref in sorted(all_pieces, key=lambda x: x.square):
        b_leg = set(before_mob[pref].legal_destinations) if pref in before_mob else set()
        a_leg = set(after_mob[pref].legal_destinations) if pref in after_mob else set()

        gained = a_leg - b_leg
        lost = b_leg - a_leg

        for dest in sorted(gained):
            mob_gained.append((pref, dest))
        for dest in sorted(lost):
            mob_lost.append((pref, dest))

    return GeometryDelta(
        appeared_attacks=app_attacks,
        disappeared_attacks=dis_attacks,
        appeared_defenses=app_defenses,
        disappeared_defenses=dis_defenses,
        appeared_rays=app_rays,
        disappeared_rays=dis_rays,
        mobility_gained=mob_gained,
        mobility_lost=mob_lost
    )
