import React from "react";
import { Button, Modal, Tabs, Tab } from "react-bootstrap";
import SarcEditor from "./SarcEditor.jsx";

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showError: false,
            errorMsg: ""
        };
        this.showError = this.showError.bind(this);
    }

    showError(errorMsg) {
        this.setState({ showError: true, errorMsg });
    }

    render() {
        return (
            <>
                <Tabs defaultActiveKey="sarc">
                    <Tab eventKey="sarc" title="SARC">
                        <SarcEditor onError={this.showError} />
                    </Tab>
                    <Tab eventKey="rstb" title="RSTB">
                        <p>Stuff</p>
                    </Tab>
                    <Tab eventKey="yaml" title="YAML">
                        <p></p>
                    </Tab>
                </Tabs>
                <Modal
                    show={this.state.showError}
                    onHide={() => this.setState({ showError: false })}
                >
                    <Modal.Header closeButton>
                        <Modal.Title>Error</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>{this.state.errorMsg}</Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="primary"
                            onClick={() => this.setState({ showError: false })}
                        >
                            Close
                        </Button>
                    </Modal.Footer>
                </Modal>
            </>
        );
    }
}

export default App;
