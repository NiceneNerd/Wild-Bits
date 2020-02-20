import React from "react";
import { Tabs, Tab } from "react-bootstrap";
import SarcEditor from "./SarcEditor.jsx";

class App extends React.Component {
    render() {
        return (
            <Tabs defaultActiveKey="sarc">
                <Tab eventKey="sarc" title="SARC">
                    <SarcEditor
                        sarc={{
                            Actor: {
                                Pack: {
                                    "Obj_SupportApp_Wind.sbactorpack": {},
                                    "GameROMPlayer.sbactorpack": {}
                                }
                            }
                        }}
                    />
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
