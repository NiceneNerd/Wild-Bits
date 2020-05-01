import React from "react";
import {
    Badge,
    Container,
    Row,
    Col,
    Button,
    ButtonGroup,
    ButtonToolbar,
    Tooltip,
    OverlayTrigger
} from "react-bootstrap";
import { FolderOpen } from "@material-ui/icons";
import AceEditor from "react-ace";
import "ace-builds/src-noconflict/mode-yaml";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/theme-pastel_on_dark";

const yamlTypes = {
    AAMP: "aamp",
    BYML: "byml",
    MSBT: "msbt"
};

class YamlEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            yaml: "",
            type: null,
            be: false,
            path: "",
            modified: false
        };
        this.open_yaml = this.open_yaml.bind(this);
    }

    open_yaml() {
        pywebview.api.open_yaml().then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
            this.setState({
                ...res,
                modified: false
            });
        });
    }

    render() {
        return (
            <Container
                fluid
                className="yaml d-flex flex-column"
                style={{ height: "100%" }}>
                <Row className="toolbar">
                    <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
                        <ButtonToolbar>
                            <ButtonGroup size="xs">
                                <Button onClick={this.open_yaml}>
                                    <FolderOpen />
                                </Button>
                            </ButtonGroup>
                        </ButtonToolbar>
                    </Col>
                    <Col>
                        <div
                            style={{
                                verticalAlign: "middle",
                                textAlign: "right"
                            }}>
                            <OverlayTrigger
                                placement="bottom"
                                overlay={
                                    <Tooltip>{this.state.path}</Tooltip> || null
                                }>
                                <Badge variant="secondary">
                                    {this.state.path
                                        ? this.state.path
                                              .replace("\\", "/")
                                              .split("/")
                                              .splice(-1)[0]
                                        : this.state.yaml
                                        ? "Unsaved File"
                                        : ""}
                                </Badge>
                            </OverlayTrigger>{" "}
                            {this.state.yaml &&
                                [yamlTypes.BYML, yamlTypes.MSBT].includes(
                                    this.state.type
                                ) && (
                                    <>
                                        {this.state.be ? (
                                            <OverlayTrigger
                                                placement="bottom"
                                                overlay={
                                                    <Tooltip>
                                                        Big Endian
                                                    </Tooltip>
                                                }>
                                                <Badge variant="info">BE</Badge>
                                            </OverlayTrigger>
                                        ) : (
                                            <OverlayTrigger
                                                placement="bottom"
                                                overlay={
                                                    <Tooltip>
                                                        Little Endian
                                                    </Tooltip>
                                                }>
                                                <Badge variant="info">LE</Badge>
                                            </OverlayTrigger>
                                        )}
                                        {"  "}
                                    </>
                                )}
                            {this.state.modified && (
                                <Badge variant="success">Modified</Badge>
                            )}
                        </div>
                    </Col>
                </Row>
                <Row
                    className="d-flex flex-column flex-grow-1"
                    style={{ height: "100%" }}>
                    <AceEditor
                        className="flex-grow-1"
                        mode="yaml"
                        theme="pastel_on_dark"
                        style={{ width: "calc(100% - 7px)" }}
                        fontSize={14}
                        showPrintMargin={false}
                        enableLiveAutocompletion={true}
                        value={this.state.yaml}
                        onChange={yaml => this.setState({ yaml })}
                    />
                </Row>
            </Container>
        );
    }
}

export default YamlEditor;
