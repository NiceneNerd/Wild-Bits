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
    FormControl,
    Form
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
            sarc: null,
            modified: false,
            path: "",
            be: false,
            selected: null,
            showRename: false,
            newName: "",
            showAdd: false,
            addName: "",
            showNew: false,
            showAdd: false
        };
        this.file_infos = {};
        this.open_sarc = this.open_sarc.bind(this);
        this.create_sarc = this.create_sarc.bind(this);
        this.save_sarc = this.save_sarc.bind(this);
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

    create_sarc() {
        pywebview.api
            .create_sarc(
                document.getElementById("new-be").checked,
                document.getElementById("new-align").value
            )
            .then(
                res =>
                    this.setState({ ...res, modified: false, showNew: false }),
                () => (this.file_infos = {})
            );
    }

    open_sarc() {
        pywebview.api.open_sarc().then(
            res => this.setState({ ...res, modified: false }),
            () => (this.file_infos = {})
        );
    }

    save_sarc(path) {
        pywebview.api.save_sarc(path || "").then(res => {
            if (res.error) {
                if (res.error != "Cancelled") this.props.onError(res.error);
                return;
            }
            this.setState({ modified: false }, () =>
                this.props.showToast("Saved")
            );
        });
    }

    extract_file() {
        pywebview.api.extract_sarc_file(this.state.selected.path).then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
            this.props.showToast(`${this.state.selected.path} extracted`);
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
        if (!this.file_infos.hasOwnProperty(path)) {
            pywebview.api.get_file_info(path, this.state.be).then(res => {
                this.setState({ selected: { path, ...res } });
                this.file_infos[path] = res;
            });
        } else {
            this.setState({ selected: { path, ...this.file_infos[path] } });
        }
    }

    render() {
        return (
            <>
                <Container fluid className="sarc">
                    <Row style={{ paddingBottom: "0.25rem" }}>
                        <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
                            <ButtonToolbar>
                                <ButtonGroup size="xs" className="mr-2">
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>New</Tooltip>}
                                    >
                                        <Button>
                                            <Create
                                                onClick={() =>
                                                    this.setState({
                                                        showNew: true
                                                    })
                                                }
                                            />
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
                                        <Button
                                            onClick={() =>
                                                this.save_sarc(this.state.path)
                                            }
                                        >
                                            <Save />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Save As...</Tooltip>}
                                    >
                                        <Button
                                            onClick={() => this.save_sarc("")}
                                        >
                                            <SaveAlt />
                                        </Button>
                                    </OverlayTrigger>
                                </ButtonGroup>
                                <ButtonGroup size="xs">
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Add File...</Tooltip>}
                                    >
                                        <Button
                                            variant="success"
                                            onClick={() =>
                                                this.setState({ showAdd: true })
                                            }
                                        >
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
                                <Badge variant="secondary">
                                    {this.state.path
                                        ? this.state.path
                                        : this.state.sarc
                                        ? "Unsaved SARC"
                                        : ""}
                                </Badge>{" "}
                                {this.state.sarc && (
                                    <>
                                        {this.state.be ? (
                                            <OverlayTrigger
                                                placement="bottom"
                                                overlay={
                                                    <Tooltip>
                                                        Big Endian
                                                    </Tooltip>
                                                }
                                            >
                                                <Badge variant="info">BE</Badge>
                                            </OverlayTrigger>
                                        ) : (
                                            <OverlayTrigger
                                                placement="bottom"
                                                overlay={
                                                    <Tooltip>
                                                        Little Endian
                                                    </Tooltip>
                                                }
                                            >
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
                    <Row style={{ flexGrow: 1, minHeight: 0 }}>
                        <Col className="tree">
                            {this.state.sarc ? (
                                <>
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
                                </>
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
                                        <>
                                            <strong>RSTB:</strong>{" "}
                                            {this.state.selected.rstb[0]}
                                        </>
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
                <Modal
                    show={this.state.showNew}
                    onHide={() => this.setState({ showNew: false })}
                >
                    <Modal.Header closeButton>
                        <Modal.Title>New SARC</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            <big>Select new SARC options:</big>
                        </p>
                        <Form>
                            <Form.Check label="Use big endian" id="new-be" />
                            <Form.Group as={Row}>
                                <Form.Label column sm={3}>
                                    Alignment (advanced)
                                </Form.Label>
                                <Col sm={9} className="mt-1">
                                    <Form.Control
                                        type="number"
                                        id="new-align"
                                        defaultValue={4}
                                    />
                                </Col>
                            </Form.Group>
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() => this.setState({ showNew: false })}
                        >
                            Close
                        </Button>
                        <Button variant="primary" onClick={this.create_sarc}>
                            Create
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Modal
                    show={this.state.showAdd}
                    onHide={() => this.setState({ showAdd: false })}
                >
                    <Modal.Header>
                        <Modal.Title>Add File to SARC</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            Select the file you wish to add to this SARC, and
                            then enter the full path at which it should be
                            added, e.g.{" "}
                            <code>Actor/ActorLink/GameROMPlayer.bxml</code>. You
                            can also use <code>//</code> to provide a path
                            inside of a nested SARC, for example,{" "}
                            <code>
                                Actor/Pack/GameROMPlayer.sbactorpack//Actor/ActorLink/GameROMPlayer.bxml
                            </code>
                            .
                        </p>
                        <Form>
                            <Form.Group as={Row}>
                                <Form.Label column sm={2}>
                                    File
                                </Form.Label>
                                <Col sm={10}>
                                    <Form.Control>
                                        <InputGroup.Append>
                                            <Button variant="secondary">
                                                Browse...
                                            </Button>
                                        </InputGroup.Append>
                                    </Form.Control>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row}>
                                <Form.Label column sm={2}>
                                    Path
                                </Form.Label>
                                <Col sm={10}>
                                    <Form.Control placeholder="Path/In/Sarc/For.File" />
                                </Col>
                            </Form.Group>
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onHide={() => this.setState({ showAdd: false })}
                        >
                            Close
                        </Button>
                        <Button variant="primary">Add</Button>
                    </Modal.Footer>
                </Modal>
            </>
        );
    }
}

export default SarcEditor;
