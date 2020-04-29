import React from "react";
import { Button, Modal, Tabs, Tab, Toast } from "react-bootstrap";
import SarcEditor from "./SarcEditor.jsx";
import RstbEditor from './RstbEditor.jsx';

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            showError: false,
            errorMsg: "",
            showToast: false,
            toastMsg: "",
            showConfirm: false,
            confirmMsg: "",
            confirmCallback: () => null
        };
        this.showError = this.showError.bind(this);
        this.showToast = this.showToast.bind(this);
        this.showConfirm = this.showConfirm.bind(this);
    }

    showError(errorMsg) {
        this.setState({ showError: true, errorMsg });
    }

    showToast(toastMsg) {
        this.setState({ showToast: true, toastMsg });
    }

    showConfirm(confirmMsg, confirmCallback) {
        this.setState({ showConfirm: true, confirmMsg, confirmCallback });
    }

    render() {
        return (
            <>
                <Tabs defaultActiveKey="sarc">
                    <Tab eventKey="sarc" title="SARC">
                        <SarcEditor
                            onError={this.showError}
                            showToast={this.showToast}
                            showConfirm={this.showConfirm}
                        />
                    </Tab>
                    <Tab eventKey="rstb" title="RSTB">
                        <RstbEditor
                            onError={this.showError}
                            showToast={this.showToast}
                            showConfirm={this.showConfirm} />
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
                <Modal
                    show={this.state.showConfirm}
                    onHide={() => this.setState({ showConfirm: false })}
                >
                    <Modal.Header closeButton>
                        <Modal.Title>Confirm</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>{this.state.confirmMsg}</Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() =>
                                this.setState({ showConfirm: false })
                            }
                        >
                            Close
                        </Button>
                        <Button
                            variant="primary"
                            onClick={() => {
                                this.state.confirmCallback();
                                this.setState({ showConfirm: false });
                            }}
                        >
                            OK
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Toast
                    show={this.state.showToast}
                    onClose={() => this.setState({ showToast: false })}
                    delay={1500}
                    autohide
                    style={{
                        position: "absolute",
                        bottom: "0.25rem",
                        left: "50%",
                        transform: "translateX(-50%)"
                    }}
                >
                    <Toast.Body>{this.state.toastMsg}</Toast.Body>
                </Toast>
            </>
        );
    }
}

export default App;
