import React from "react";
import {
    Badge,
    Button,
    ButtonGroup,
    ButtonToolbar,
    Container,
    Col,
    OverlayTrigger,
    Row,
    Tooltip
} from "react-bootstrap";
import { TreeView, TreeItem } from "@material-ui/lab";
import {
    Add,
    Create,
    FileCopy,
    Folder,
    FolderOpen,
    Archive,
    Unarchive,
    Save,
    SaveAlt
} from "@material-ui/icons";

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
            be: false,
            selected: null
        };
        this.open_sarc = this.open_sarc.bind(this);
        this.extract_file = this.extract_file.bind(this);
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
        const full_path = path.join("/");
        return (
            <TreeItem
                key={full_path}
                nodeId={full_path}
                expandIcon={
                    type == "folder" ? (
                        <Folder fontSize="small" />
                    ) : type == "sarc" ? (
                        <Archive fontSize="small" />
                    ) : null
                }
                collapseIcon={
                    type == "folder" ? (
                        <FolderOpen fontSize="small" />
                    ) : type == "sarc" ? (
                        <Unarchive fontSize="small" />
                    ) : null
                }
                label={
                    <span style={{ verticalAlign: "text-top" }}>{file}</span>
                }
                path={full_path}
                type={type}
                onClick={
                    type != "folder"
                        ? () => this.handleSelect(full_path)
                        : () => this.setState({ selected: null })
                }
            >
                {Object.keys(children).map(file =>
                    this.render_node(file, children[file], path.slice(0))
                )}
            </TreeItem>
        );
    }

    open_sarc() {
        pywebview.api.open_sarc().then(res => this.setState({ ...res }));
    }

    extract_file(path) {
        pywebview.api.extract_sarc_file(path).then(res => {
            if (res.error) {
                this.onError(res.error);
            }
        });
    }

    handleSelect(path) {
        pywebview.api
            .get_file_info(path, this.state.be)
            .then(res => this.setState({ selected: res }));
    }

    render() {
        return (
            <Container fluid className="sarc">
                <Row>
                    <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
                        <ButtonToolbar>
                            <ButtonGroup size="xs">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>New</Tooltip>}
                                >
                                    <Button>
                                        <Create />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Open a SARC...</Tooltip>}
                                >
                                    <Button onClick={this.open_sarc}>
                                        <FolderOpen />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Save</Tooltip>}
                                >
                                    <Button>
                                        <Save />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Save As...</Tooltip>}
                                >
                                    <Button>
                                        <SaveAlt />
                                    </Button>
                                </OverlayTrigger>
                            </ButtonGroup>
                            <span>&nbsp;&nbsp;</span>
                            <ButtonGroup size="xs">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Add File...</Tooltip>}
                                >
                                    <Button variant="success">
                                        <Add />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={
                                        <Tooltip>Update from Folder...</Tooltip>
                                    }
                                >
                                    <Button variant="success">
                                        <FileCopy />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Extract SARC...</Tooltip>}
                                >
                                    <Button variant="success">
                                        <Unarchive />
                                    </Button>
                                </OverlayTrigger>
                            </ButtonGroup>
                        </ButtonToolbar>
                    </Col>
                    <Col>{this.state.path}</Col>
                </Row>
                <Row style={{ flexGrow: 1, minHeight: 0 }}>
                    <Col className="tree">
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
                    <Col xs={4} className="file-actions">
                        <Container>
                            <Row>
                                <Col>
                                    <Button
                                        disabled={
                                            !this.state.selected ||
                                            !this.state.selected.is_yaml
                                        }
                                    >
                                        Edit
                                    </Button>
                                </Col>
                                <Col>
                                    <Button onClick={this.extract_file}>
                                        Extract
                                    </Button>
                                </Col>
                            </Row>
                            <Row>
                                <Col>
                                    <Button>Rename</Button>
                                </Col>
                                <Col>
                                    <Button>Delete</Button>
                                </Col>
                            </Row>
                        </Container>
                        {this.state.selected != null && (
                            <div>
                                <div className="filename">
                                    <strong>{this.state.selected.file}</strong>{" "}
                                    {this.state.selected.modified && (
                                        <Badge variant="warning">
                                            Modified
                                        </Badge>
                                    )}
                                </div>
                                <strong>File Size:</strong>{" "}
                                {this.state.selected.size}
                                <br />
                                {this.state.selected.modified && (
                                    <React.Fragment>
                                        <strong>RSTB:</strong>{" "}
                                        {this.state.selected.rstb[0]}
                                    </React.Fragment>
                                )}
                            </div>
                        )}
                    </Col>
                </Row>
            </Container>
        );
    }
}

export default SarcEditor;
