import './App.css';
import {BrowserRouter as Router, Route, Routes} from "react-router-dom";
import Home from "../Home/Home";
import VideoPlayer from "../VideoPlayer/VideoPlayer";

function App() {
  return (
      <Router>
        <Routes>
            <Route path="*" element={<Home/>}/>
            <Route path="/video/:filename" component={<VideoPlayer/>}/>
        </Routes>
      </Router>

  );
}

export default App;
