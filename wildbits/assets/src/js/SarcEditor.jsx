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
    Tooltip,
    Modal,
    InputGroup,
    FormControl
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
            modified: false,
            path: "",
            be: false,
            selected: null,
            showRename: false,
            newName: ""
        };
        this.file_infos = {};
        this.open_sarc = this.open_sarc.bind(this);
        this.extract_file = this.extract_file.bind(this);
        this.rename_file = this.rename_file.bind(this);
        this.delete_file = this.delete_file.bind(this);
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
        pywebview.api.open_sarc().then(
            res => this.setState({ ...res, modified: false }),
            () => (this.file_infos = {})
        );
    }

    extract_file() {
        pywebview.api.extract_sarc_file(this.state.selected.path).then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
        });
    }

    rename_file() {
        pywebview.api
            .rename_sarc_file(this.state.selected.path, this.state.newName)
            .then(res => {
                this.setState({ showRename: false });
                if (res.error) {
                    this.props.onError(res.error);
                    return;
                }
                this.setState({ sarc: res, modified: true }, () =>
                    this.props.showToast(`Rename successful`)
                );
            });
    }

    delete_file() {
        const file = this.state.selected.file;
        this.props.showConfirm(
            `Are you sure you want to delete ${file}?`,
            () => {
                pywebview.api
                    .delete_sarc_file(this.state.selected.path)
                    .then(res => {
                        if (res.error) {
                            this.props.onError(res.error);
                            return;
                        }
                        this.setState({ sarc: res, modified: true }, () =>
                            this.props.showToast(`Deleted ${file}`)
                        );
                    });
            }
        );
    }

    handleSelect(path) {
        pywebview.api
            .get_file_info(path, this.state.be)
            .then(res => this.setState({ selected: { path, ...res } }));
    }

    render() {
        return (
            <>
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
                                        overlay={
                                            <Tooltip>Open a SARC...</Tooltip>
                                        }
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
                                            <Tooltip>
                                                Update from Folder...
                                            </Tooltip>
                                        }
                                    >
                                        <Button variant="success">
                                            <FileCopy />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={
                                            <Tooltip>Extract SARC...</Tooltip>
                                        }
                                    >
                                        <Button variant="success">
                                            <Unarchive />
                                        </Button>
                                    </OverlayTrigger>
                                </ButtonGroup>
                            </ButtonToolbar>
                        </Col>
                        <Col>
                            <div
                                style={{
                                    verticalAlign: "middle",
                                    textAlign: "right"
                                }}
                            >
                                <small class="text-secondary">
                                    {this.state.path}
                                </small>{" "}
                                {this.state.modified && (
                                    <Badge variant="success">Modified</Badge>
                                )}
                            </div>
                        </Col>
                    </Row>
                    <Row style={{ flexGrow: 1, minHeight: 0 }}>
                        <Col className="tree">
                            {Object.keys(this.state.sarc) ? (
                                <React.Fragment>
                                    <TreeView>
                                        {Object.keys(
                                            this.state.sarc
                                        ).map(file =>
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
                                        <Button
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={this.extract_file}
                                        >
                                            Extract
                                        </Button>
                                    </Col>
                                </Row>
                                <Row>
                                    <Col>
                                        <Button
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={() =>
                                                this.setState({
                                                    showRename: true
                                                })
                                            }
                                        >
                                            Rename
                                        </Button>
                                    </Col>
                                    <Col>
                                        <Button
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={this.delete_file}
                                        >
                                            Delete
                                        </Button>
                                    </Col>
                                </Row>
                            </Container>
                            {this.state.selected != null && (
                                <div>
                                    <div className="filename">
                                        <strong>
                                            {this.state.selected.file}
                                        </strong>{" "}
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
                <Modal
                    show={this.state.showRename}
                    onHide={() => this.setState({ showRename: false })}
                >
                    <Modal.Header closeButton>
                        <Modal.Title>Rename File</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            <big>Rename {this.state.selected?.file}:</big>
                        </p>
                        <InputGroup className="mb-3">
                            <InputGroup.Prepend>
                                <InputGroup.Text>New name</InputGroup.Text>
                            </InputGroup.Prepend>
                            <FormControl
                                value={this.state.newName}
                                onChange={e =>
                                    this.setState({
                                        newName: e.currentTarget.value
                                    })
                                }
                            />
                        </InputGroup>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() => this.setState({ showRename: false })}
                        >
                            Close
                        </Button>
                        <Button variant="primary" onClick={this.rename_file}>
                            Rename
                        </Button>
                    </Modal.Footer>
                </Modal>
            </>
        );
    }
}

export default SarcEditor;
