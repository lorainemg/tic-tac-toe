import './App.css';
import {useState} from 'react';


function Square({value, onSquareClick, winner}) {
    return <button className="square" onClick={onSquareClick}
                   style={winner ? {"border": "2px solid black"} : {}}>{value}</button>
}

function Board({xIsNext, squares, onPlay}) {

    function handleClick(i) {
        if (squares[i] || winner)  // if square is already filled or there is a winner, do nothing
            return

        const nextSquares = squares.slice();
        nextSquares[i] = xIsNext ? "X" : "O";
        onPlay(nextSquares, i)
    }

    const winner = calculateWinner(squares);
    let status = winner ? "Winner: " + squares[winner[0]] : "Next player: " + (xIsNext ? "X" : "O")

    return (
        <>
            <div className="status">{status}</div>
            {[0, 1, 2].map((row) => {
                return (
                    <div key={row} className="board-row">
                        {[0, 1, 2].map((col) => {
                            return <Square key={col} value={squares[row * 3 + col]}
                                           winner={winner && winner.includes(row * 3 + col)}
                                           onSquareClick={() => handleClick(row * 3 + col)}/>
                        })}
                    </div>
                )
            })}
        </>
    );
}


export default function Game() {
    const [history, setHistory] = useState([Array(9).fill(null)]);
    const [currentMove, setCurrentMove] = useState(0);
    const [movementHistory, setMovementHistory] = useState([]);
    const currentSquares = history[currentMove];
    const xIsNext = currentMove % 2 === 0;

    function handlePlay(nextSquares, idx) {
        const nextHistory = [...history.slice(0, currentMove + 1), nextSquares];
        setHistory(nextHistory);
        setMovementHistory([...movementHistory, `(${Math.floor(idx / 3) + 1}, ${idx % 3 + 1})`]);
        setCurrentMove(nextHistory.length - 1);
    }

    function jumpTo(nextMove) {
        setCurrentMove(nextMove);
    }

    const moves = history.map((squares, move) => {
        let description = move > 0 ? 'Go to move ' + movementHistory[move] : 'Go to game start';
        return (
            <li key={move}>
                {move === currentMove ? <span className="bold">You are at move {movementHistory[move]}</span> : <button
                    onClick={() => jumpTo(move)}>{description}</button>}
            </li>
        );
    });
    return (
        <div className="game">
            <div className="game-board">
                <Board xIsNext={xIsNext} squares={currentSquares} onPlay={handlePlay}/>
            </div>
            <div className="game-info">
                <ol>{moves}</ol>
            </div>
        </div>
    );
}

function calculateWinner(squares) {
    const lines = [
        [0, 1, 2],
        [3, 4, 5],
        [6, 7, 8],
        [0, 3, 6],
        [1, 4, 7],
        [2, 5, 8],
        [0, 4, 8],
        [2, 4, 6]
    ];
    for (let i = 0; i < lines.length; i++) {
        const [a, b, c] = lines[i];
        if (squares[a] && squares[a] === squares[b] && squares[a] === squares[c]) {
            return [a, b, c];
        }
    }
    return null;
}