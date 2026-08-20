import chess
import chess.engine
print(dir(chess.engine.Option))

b = chess.Board("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")
b.push(chess.Move.from_uci("e2e4"))
print("Board history length:", len(b.move_stack))
child = chess.Board(b.fen())
print("Reconstructed FEN board history length:", len(child.move_stack))

print("Option.is_managed in dir?:", hasattr(chess.engine.Option, 'is_managed'))
