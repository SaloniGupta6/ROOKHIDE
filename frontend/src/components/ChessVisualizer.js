import React, { useState } from 'react';
import { Chess } from 'chess.js';
import { Chessboard } from 'react-chessboard';

const ChessVisualizer = () => {
  const [game, setGame] = useState(new Chess());
  const [pgnInput, setPgnInput] = useState('');
  const [currentMoveIndex, setCurrentMoveIndex] = useState(0);
  const [gameHistory, setGameHistory] = useState([]);
  const [gameHeaders, setGameHeaders] = useState({});
  const [analysisMode, setAnalysisMode] = useState(false);

  const loadPgn = () => {
    if (!pgnInput.trim()) {
      alert('Please enter a PGN');
      return;
    }

    try {
      const newGame = new Chess();
      const result = newGame.loadPgn(pgnInput);
      
      if (result) {
        setGame(newGame);
        
        // Extract game headers
        const headers = {};
        const pgnLines = pgnInput.split('\n');
        pgnLines.forEach(line => {
          const match = line.match(/\[(\w+)\s+"(.+)"\]/);
          if (match) {
            headers[match[1]] = match[2];
          }
        });
        setGameHeaders(headers);

        // Get move history
        const history = newGame.history({ verbose: true });
        setGameHistory(history);
        setCurrentMoveIndex(history.length);
        
        alert('PGN loaded successfully!');
      } else {
        alert('Invalid PGN format');
      }
    } catch (error) {
      alert('Error loading PGN: ' + error.message);
    }
  };

  const resetGame = () => {
    const newGame = new Chess();
    setGame(newGame);
    setCurrentMoveIndex(0);
    setGameHistory([]);
    setGameHeaders({});
  };

  const goToMove = (moveIndex) => {
    try {
      const newGame = new Chess();
      
      // Play moves up to the specified index
      for (let i = 0; i < moveIndex && i < gameHistory.length; i++) {
        newGame.move(gameHistory[i]);
      }
      
      setGame(newGame);
      setCurrentMoveIndex(moveIndex);
    } catch (error) {
      console.error('Error navigating to move:', error);
    }
  };

  const previousMove = () => {
    if (currentMoveIndex > 0) {
      goToMove(currentMoveIndex - 1);
    }
  };

  const nextMove = () => {
    if (currentMoveIndex < gameHistory.length) {
      goToMove(currentMoveIndex + 1);
    }
  };

  const handlePieceClick = (piece) => {
    if (analysisMode) {
      // In analysis mode, allow free exploration
      console.log('Clicked piece:', piece);
    }
  };

  const loadSamplePgn = () => {
    const samplePgn = `[Event "Encoded Game"]
[Site "Chess Steganography DApp"]
[Date "2024.03.10"]
[Round "1"]
[White "Alice"]
[Black "Bob"]
[Result "1/2-1/2"]
[Seed "123456"]
[DataBitLength "192"]

1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 5. O-O Be7 6. Re1 b5 
7. Bb3 d6 8. c3 O-O 9. h3 Bb7 10. d4 Re8 11. Nbd2 Bf8 12. a4 h6 
13. Bc2 exd4 14. cxd4 Nb4 15. Bb1 c5 16. d5 Nd7 17. Ra3 f5 
18. Rae3 Nf6 19. Nh2 fxe4 20. Nxe4 Nxe4 21. Rxe4 Rxe4 22. Bxe4 1/2-1/2`;
    
    setPgnInput(samplePgn);
  };

  return (
    <div className="max-w-6xl mx-auto">
      <h1 className="text-3xl font-bold text-center mb-8">Chess Game Visualizer</h1>
      
      <div className="grid md:grid-cols-2 gap-8">
        {/* Chess Board */}
        <div className="bg-white rounded-lg shadow-lg p-6">
          <div className="mb-4 flex justify-between items-center">
            <h2 className="text-xl font-semibold">Game Board</h2>
            <div className="flex items-center space-x-2">
              <label className="flex items-center space-x-2">
                <input 
                  type="checkbox" 
                  checked={analysisMode}
                  onChange={(e) => setAnalysisMode(e.target.checked)}
                  className="rounded"
                />
                <span className="text-sm">Analysis Mode</span>
              </label>
            </div>
          </div>
          
          <div className="mb-4">
            <Chessboard 
              position={game.fen()} 
              boardWidth={400}
              onPieceClick={handlePieceClick}
              arePiecesDraggable={analysisMode}
            />
          </div>

          {/* Navigation Controls */}
          <div className="flex justify-center space-x-2 mb-4">
            <button
              onClick={() => goToMove(0)}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
              disabled={currentMoveIndex === 0}
            >
              ⏮️ Start
            </button>
            <button
              onClick={previousMove}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
              disabled={currentMoveIndex === 0}
            >
              ⏪ Prev
            </button>
            <button
              onClick={nextMove}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
              disabled={currentMoveIndex >= gameHistory.length}
            >
              Next ⏩
            </button>
            <button
              onClick={() => goToMove(gameHistory.length)}
              className="px-3 py-1 bg-gray-200 hover:bg-gray-300 rounded text-sm"
              disabled={currentMoveIndex >= gameHistory.length}
            >
              End ⏭️
            </button>
          </div>

          <div className="text-center text-sm text-gray-600">
            Move {currentMoveIndex} of {gameHistory.length}
          </div>
        </div>

        {/* PGN Input and Game Info */}
        <div className="space-y-6">
          {/* PGN Input */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Load PGN</h2>
            <textarea
              value={pgnInput}
              onChange={(e) => setPgnInput(e.target.value)}
              placeholder="Paste your PGN here..."
              className="w-full h-40 p-3 border border-gray-300 rounded resize-none focus:ring-2 focus:ring-blue-500 focus:border-transparent font-mono text-sm"
            />
            <div className="mt-4 space-y-2">
              <div className="flex space-x-2">
                <button
                  onClick={loadPgn}
                  className="bg-blue-500 text-white px-4 py-2 rounded hover:bg-blue-600 transition-colors"
                >
                  Load PGN
                </button>
                <button
                  onClick={loadSamplePgn}
                  className="bg-green-500 text-white px-4 py-2 rounded hover:bg-green-600 transition-colors"
                >
                  Load Sample
                </button>
                <button
                  onClick={resetGame}
                  className="bg-gray-500 text-white px-4 py-2 rounded hover:bg-gray-600 transition-colors"
                >
                  Reset
                </button>
              </div>
            </div>
          </div>

          {/* Game Headers */}
          {Object.keys(gameHeaders).length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Game Information</h2>
              <div className="space-y-2">
                {Object.entries(gameHeaders).map(([key, value]) => (
                  <div key={key} className="flex justify-between">
                    <span className="font-medium text-gray-700">{key}:</span>
                    <span className="text-gray-900 font-mono text-sm">{value}</span>
                  </div>
                ))}
              </div>
              
              {/* Special indicators for encoded games */}
              {gameHeaders.Seed && (
                <div className="mt-4 p-3 bg-blue-50 border border-blue-200 rounded">
                  <div className="flex items-center space-x-2">
                    <span className="text-blue-500">🔐</span>
                    <span className="text-blue-800 font-medium">Encoded Game Detected</span>
                  </div>
                  <p className="text-blue-700 text-sm mt-1">
                    This game may contain hidden data in its move sequence.
                  </p>
                </div>
              )}
              
              {gameHeaders.ExpiryTime && (
                <div className="mt-2 p-3 bg-yellow-50 border border-yellow-200 rounded">
                  <div className="flex items-center space-x-2">
                    <span className="text-yellow-500">⏰</span>
                    <span className="text-yellow-800 font-medium">Self-Destructing Message</span>
                  </div>
                  <p className="text-yellow-700 text-sm mt-1">
                    Expires: {gameHeaders.ExpiryTimeReadable || gameHeaders.ExpiryTime}
                  </p>
                </div>
              )}
            </div>
          )}

          {/* Move List */}
          {gameHistory.length > 0 && (
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h2 className="text-xl font-semibold mb-4">Move History</h2>
              <div className="max-h-48 overflow-y-auto">
                <div className="grid grid-cols-2 gap-2 text-sm">
                  {gameHistory.map((move, index) => (
                    <button
                      key={index}
                      onClick={() => goToMove(index + 1)}
                      className={`text-left p-2 rounded hover:bg-gray-100 transition-colors ${
                        index + 1 === currentMoveIndex ? 'bg-blue-100 border border-blue-300' : ''
                      }`}
                    >
                      <span className="text-gray-500">{Math.floor(index / 2) + 1}{index % 2 === 0 ? '.' : '...'}</span>
                      <span className="ml-2 font-mono">{move.san}</span>
                    </button>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Game Status */}
          <div className="bg-white rounded-lg shadow-lg p-6">
            <h2 className="text-xl font-semibold mb-4">Game Status</h2>
            <div className="space-y-2 text-sm">
              <div className="flex justify-between">
                <span>Position:</span>
                <span className="font-mono text-xs">{game.fen()}</span>
              </div>
              <div className="flex justify-between">
                <span>Turn:</span>
                <span>{game.turn() === 'w' ? 'White' : 'Black'}</span>
              </div>
              <div className="flex justify-between">
                <span>Status:</span>
                <span>
                  {game.isGameOver() ? (
                    game.isCheckmate() ? 'Checkmate' :
                    game.isDraw() ? 'Draw' : 'Game Over'
                  ) : game.isCheck() ? 'Check' : 'Active'}
                </span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default ChessVisualizer;
