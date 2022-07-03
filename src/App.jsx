import { Button, Modal, Spinner, Tab, Tabs, Toast } from "react-bootstrap";
import { invoke } from "@tauri-apps/api/tauri";

import React from "react";
import RstbEditor from "./RstbEditor.jsx";
import SarcEditor from "./SarcEditor.jsx";
import YamlEditor from "./YamlEditor.jsx";

class App extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            openTab: "sarc",
            showError: false,
            loading: false,
            errorMsg: "",
            showToast: false,
            toastMsg: "",
            showConfirm: false,
            confirmMsg: "",
            confirmCallback: () => null
        };
        window.setTab = this.setTab;
        this.yamlRef = React.createRef();
        this.sarcRef = React.createRef();
        // document.oncontextmenu = () => false;
    }

    componentDidMount = async () => {
        let hasArgs = invoke("has_args");
        if (hasArgs) {
            this.setLoading(true);
            let argFile = await invoke("open_args");
            if (!argFile) return;
            switch (argFile.type) {
                case "yaml":
                    this.setTab("yaml");
                    window.openYaml({ ...argFile.data, path: argFile.path });
                    break;
                case "sarc":
                    this.setTab("sarc");
                    window.openSarc({ ...argFile.data, path: argFile.path });
                    break;
                case "rstb":
                    this.setTab("rstb");
                    console.log(argFile.data);
                    window.openRstb({ ...argFile.data, path: argFile.path });
                    break;
                default:
                    break;
            }
            this.setLoading(false);
        }
    };

    setTab = tab => {
        this.setState({ openTab: tab });
    };

    setLoading = yea => {
        this.setState({ loading: yea });
    };

    showError = error => {
        this.setState({ showError: true, errorMsg: error.message });
        console.error(error.backtrace);
    };

    showToast = toastMsg => {
        this.setState({ showToast: true, toastMsg });
    };

    showConfirm = (confirmMsg, confirmCallback) => {
        this.setState({ showConfirm: true, confirmMsg, confirmCallback });
    };

    passFile = res => {
        this.yamlRef.current.open_sarc_yaml(res);
        this.setTab("yaml");
    };
    passMod = file => this.sarcRef.current.yaml_modified(file);

    render = () => {
        return (
            <>
                <Tabs activeKey={this.state.openTab} onSelect={this.setTab}>
                    <Tab eventKey="sarc" title="SARC">
                        <SarcEditor
                            onError={this.showError}
                            setLoading={this.setLoading}
                            showToast={this.showToast}
                            showConfirm={this.showConfirm}
                            passFile={this.passFile}
                            ref={this.sarcRef}
                        />
                    </Tab>
                    <Tab eventKey="rstb" title="RSTB">
                        <RstbEditor
                            setLoading={this.setLoading}
                            onError={this.showError}
                            showToast={this.showToast}
                            showConfirm={this.showConfirm}
                        />
                    </Tab>
                    <Tab eventKey="yaml" title="YAML">
                        <YamlEditor
                            setLoading={this.setLoading}
                            onError={this.showError}
                            showToast={this.showToast}
                            showConfirm={this.showConfirm}
                            passMod={this.passMod}
                            ref={this.yamlRef}
                        />
                    </Tab>
                </Tabs>
                <Modal
                    show={this.state.showError}
                    onHide={() => this.setState({ showError: false })}>
                    <Modal.Header closeButton>
                        <Modal.Title>Error</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>{this.state.errorMsg}</Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="primary"
                            onClick={() => this.setState({ showError: false })}>
                            Close
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Modal
                    show={this.state.showConfirm}
                    onHide={() => this.setState({ showConfirm: false })}>
                    <Modal.Header closeButton>
                        <Modal.Title>Confirm</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <div
                            dangerouslySetInnerHTML={{
                                __html: this.state.confirmMsg
                            }}></div>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() =>
                                this.setState({ showConfirm: false })
                            }>
                            Close
                        </Button>
                        <Button
                            variant="primary"
                            onClick={() => {
                                this.state.confirmCallback();
                                this.setState({ showConfirm: false });
                            }}>
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
                    }}>
                    <Toast.Body>{this.state.toastMsg}</Toast.Body>
                </Toast>
                {this.state.loading && (
                    <div className="loader">
                        <Spinner animation="border" />
                    </div>
                )}
            </>
        );
    };
}

export default App;
