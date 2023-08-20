import React, { Component, useState } from "react";
import Crossword from "@jaredreisinger/react-crossword";
const GENERATE_CROSSWORD_CODE = `
from platyrhynchos.scripts import simulated_annealing_routine
from platyrhynchos.exclusive import get_regex_w_alphabit
from json import dumps

if await get_regex_w_alphabit(".+", "11111111111111111111111111", ""):
    print("Connection to DB via Pyodide successful!")

dumps(await simulated_annealing_routine())
`;

let worker_request_id = 0;
const worker: Worker = new Worker(new URL("./py-worker.js", import.meta.url));
type CrosswordResultObject = {
  down: {
    [key: number]: {
      answer: string;
      clue: string;
      row: number;
      col: number;
    };
  };
  across: {
    [key: number]: {
      answer: string;
      clue: string;
      row: number;
      col: number;
    };
  };
};

function App() {
  const [crossword, setCrossword] = useState<CrosswordResultObject | null>(
    null
  );
  const [worker_response_id, setWorkerResponseId] = useState<number>(
    worker_request_id++
  );

  worker.onmessage = (event) => {
    if (event.data.request_id === worker_response_id) {
      let result = JSON.parse(event.data.result);
      setCrossword(result);
    }
  };

  if (crossword === null && worker_response_id === 1) {
    worker.postMessage({
      request_id: worker_response_id,
      code_to_run: GENERATE_CROSSWORD_CODE,
    });
    return (
      <div className="App">
        <h1>Pls wait</h1>
      </div>
    );
  } else if (worker_response_id === 1) {
    return (
      <div className="App">
        <h1>Pls wait</h1>
      </div>
    );
  } else {
    return (
      <div className="App">
        <Crossword data={crossword} />
      </div>
    );
  }
}

export default App;
