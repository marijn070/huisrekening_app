import "./global.css";
import { Route, Routes } from "react-router-dom";
import Main from "./main/Main";
import Sidebar from "./sidebar/Sidebar";
import Roommates from "./Roommates";
import Rooms from "./Rooms";
import { library } from "@fortawesome/fontawesome-svg-core";
import { fas } from "@fortawesome/free-solid-svg-icons";
library.add(fas);

const App = () => {
  return (
    <div className="app">
      <Sidebar />
      <Routes>
        <Route element={<Main />}>
          <Route path="/roommates" element={<Roommates />} />
        </Route>
      </Routes>
    </div>
  );
};

export default App;
