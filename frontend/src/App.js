import React from 'react';
import {BrowserRouter as Router, Route, Switch} from 'react-router-dom';
import './index.css';
import Main from './component/Main';
import FileUpload from './component/FileUpload';

function App() {
  return (
    <div> 
    <Router>
        <div className="container">
          <Switch>
            <Route path = "/"component={Main} exact={true} />
            <Route path="/file" component={FileUpload} exact={true} />
          render={({ location }) => (
            <div>
              <h2>ERROR</h2>
              <h2>이 페이지는 존재하지 않습니다.</h2>
            </div>
          )}
        </Switch>
      </div>
    </Router>
  </div>
  );
}

export default App;