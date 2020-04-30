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
import "ace-builds/src-noconflict/theme-clouds_midnight";

const yamlTypes = {
    AAMP: "aamp",
    BYML: "byml",
    MSYT: "msyt"
};

class YamlEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            yaml: "",
            type: null,
            be: false,
            modified: false
        };
    }

    render() {
        return (
            <Container fluid className="yaml">
                <Row className="toolbar">
                    <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
                        <ButtonToolbar>
                            <ButtonGroup size="xs">
                                <Button>
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
                                [yamlTypes.BYML, yamlTypes.MSYT].includes(
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
                <Row>
                    <AceEditor mode="yaml" theme="clouds_midnight" />
                </Row>
            </Container>
        );
    }
}

export default YamlEditor;
