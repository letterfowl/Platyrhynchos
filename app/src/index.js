import { initDatabase } from "./duck.js";
import { initPy } from "./loadpy.js"

initDatabase().then((db) => {
    console.log(db)
}
)
initPy().then((py) => {
    console.log(py)
}
)
