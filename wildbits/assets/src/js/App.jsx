import React from "react";
import { Tabs, Tab } from "react-bootstrap";

class App extends React.Component {
  render() {
    return (
      <Tabs defaultActiveKey="sarc">
        <Tab eventKey="sarc" title="SARC">
          <p>
            It's Wild Bits, but with React and <code>oead</code>
          </p>
        </Tab>
        <Tab eventKey="rstb" title="RSTB">
          <p>Stuff</p>
        </Tab>
        <Tab eventKey="yaml" title="YAML">
          <p></p>
        </Tab>
      </Tabs>
    );
  }
}

export default App;
