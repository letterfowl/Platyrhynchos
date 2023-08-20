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

let worker_request_id = 1;
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
  const [gen_finished, setGenFinished] = useState<boolean>(false);
  let [worker_response_id, setWorkerResponseId] = useState<number>(0);

  worker.onmessage = (event) => {
    if (event.data.request_id === worker_response_id) {
      let result = JSON.parse(event.data.result);
      window.open("data:text/json;charset=utf-8," + encodeURIComponent(event.data.result));
      setGenFinished(true);
      setCrossword(result);
    }
  };

  if (worker_response_id === 0 && !gen_finished) {
    worker.postMessage({
      request_id: worker_request_id,
      code_to_run: GENERATE_CROSSWORD_CODE,
    });
    worker_response_id = worker_request_id;
    worker_request_id++;
    console.log("Changed worker_response_id:", worker_response_id);
  }
  if (!gen_finished) {
    return (
      <div className="App">
        <h1>Pls wait</h1>
      </div>
    );
  } else if (crossword === null && gen_finished) {
    return (
      <div className="App">
        <h1>Failed to generate a crossword</h1>
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
