import React from "react";
import { Button, Container, Col, Row } from "react-bootstrap";
import { TreeView, TreeItem } from "@material-ui/lab";
import { Folder, FolderOpen, Archive, Unarchive } from "@material-ui/icons";

const SARC_EXTS = [
    "sarc",
    "pack",
    "bactorpack",
    "bmodelsh",
    "beventpack",
    "stera",
    "stats",
    "ssarc",
    "spack",
    "sbactorpack",
    "sbmodelsh",
    "sbeventpack",
    "sstera",
    "sstats",
    "sblarc",
    "blarc",
    "sbfarc",
    "bfarc"
];

class SarcEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            sarc: {},
            path: "",
            be: false
        };
        this.open_sarc = this.open_sarc.bind(this);
    }

    open_sarc() {
        pywebview.api.open_sarc().then(res => console.log(res));
    }

    render_node(file, children, path) {
        let type;
        if (!file.includes(".")) {
            type = "folder";
        } else {
            const ext = file.split(".").slice(-1)[0];
            if (SARC_EXTS.includes(ext)) {
                type = "sarc";
            } else {
                type = "file";
            }
        }
        if (!path) {
            path = [file];
        } else {
            path.push(type != "sarc" ? file : `${file}/`);
        }
        return (
            <TreeItem
                key={file}
                nodeId={file}
                expandIcon={
                    type == "folder" ? (
                        <Folder fontSize="small" />
                    ) : type == "sarc" ? (
                        <Unarchive fontSize="small" />
                    ) : null
                }
                collapseIcon={
                    type == "folder" ? (
                        <FolderOpen fontSize="small" />
                    ) : type == "sarc" ? (
                        <Archive fontSize="small" />
                    ) : null
                }
                label={
                    <span style={{ verticalAlign: "text-top" }}>{file}</span>
                }
                path={path.join("/")}
                type={type}
            >
                {Object.keys(children).map(file =>
                    this.render_node(file, children[file], path.slice(0))
                )}
            </TreeItem>
        );
    }

    render() {
        return (
            <Container
                fluid
                className="sarc"
                style={{ display: "flex", flexDirection: "column" }}
            >
                <Row>
                    <Col>
                        {Object.keys(this.state.sarc) ? (
                            <React.Fragment>
                                <TreeView>
                                    {Object.keys(this.state.sarc).map(file =>
                                        this.render_node(
                                            file,
                                            this.state.sarc[file]
                                        )
                                    )}
                                </TreeView>
                            </React.Fragment>
                        ) : (
                            <p>No SARC open</p>
                        )}
                    </Col>
                    <Col xs={3} className="file-actions">
                        <Button>Open as YAML</Button>
                        <Button>Extract</Button>
                        <Button>Rename</Button>
                        <Button>Delete</Button>
                    </Col>
                </Row>
                <Row>
                    <Col>
                        <Button onClick={this.open_sarc}>Open</Button>
                        <Button>Save</Button>
                        <Button>Save As</Button>
                    </Col>
                </Row>
            </Container>
        );
    }
}

export default SarcEditor;
