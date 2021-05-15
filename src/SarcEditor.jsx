import {
    Add,
    Archive,
    Create,
    FileCopy,
    Folder,
    FolderOpen,
    Save,
    SaveAlt,
    Unarchive
} from "@material-ui/icons";
import {
    Badge,
    Button,
    ButtonGroup,
    ButtonToolbar,
    Col,
    Container,
    Form,
    FormControl,
    InputGroup,
    Modal,
    OverlayTrigger,
    Row,
    Tooltip
} from "react-bootstrap";
import { TreeItem, TreeView } from "@material-ui/lab";
import { open, save } from "@tauri-apps/api/dialog";

import React from "react";
import { invoke } from "@tauri-apps/api/tauri";

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
            modded: [],
            path: "",
            be: false,
            selected: null,
            showRename: false,
            newName: "",
            showAdd: false,
            addName: "",
            showNew: false,
            showAdd: false,
            addFile: "",
            addPath: ""
        };
        this.file_infos = {};
        window.openSarc = this.open;
    }

    yaml_modified = file =>
        this.setState({
            modified: true,
            modded: [...this.state.modded.filter(f => f != file), file]
        });

    render_node = (file, children, path) => {
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
                className={
                    this.state.modded.includes(full_path)
                        ? "bg-warning text-dark"
                        : ""
                }
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
                }>
                {Object.keys(children).map(file =>
                    this.render_node(file, children[file], path.slice(0))
                )}
            </TreeItem>
        );
    };

    create_sarc = async () => {
        const res = await pywebview.api.create_sarc(
            document.getElementById("new-be1").checked,
            document.getElementById("new-align").value
        );
        this.setState(
            { ...res, modified: false, showNew: false },
            () => (this.file_infos = {})
        );
    };

    open = data => {
        this.setState({ ...data, modified: false });
        this.file_infos = {};
    };

    open_sarc = async () => {
        const file = await open();
        if (!file) return;
        this.props.setLoading(true);
        try {
            const res = await invoke("open_sarc", { file });
            this.setState({ path: file }, () => this.open(res));
        } catch(err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    save_sarc = async file => {
        if (!file) {
            file = await save();
            if (!file) return;
        }
        this.props.setLoading(true);
        try {
            await invoke("save_sarc", { file });
            this.setState({ modified: false, path: file }, () => this.props.showToast("Saved"));
        } catch(err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    add_file = async () => {
        const file = this.state.addFile.split(/[\\\/]/).slice(-1)[0];
        const res = await pywebview.api.add_sarc_file(
            this.state.addFile,
            this.state.addPath
        );
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.setState(
            {
                sarc: res[0],
                modded: res[1],
                modified: true,
                showAdd: false,
                addFile: "",
                addPath: ""
            },
            () => this.props.showToast(`Added ${file} to SARC`)
        );
    };

    update_folder = async () => {
        const res = await pywebview.api.update_sarc_folder();
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.setState({ sarc: res[0], modded: res[1], modified: true }, () =>
            this.props.showToast("SARC updated")
        );
    };

    extract_sarc = async () => {
        const res = await pywebview.api.extract_sarc();
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.props.showToast("All files in SARC extracted");
    };

    extract_file = async () => {
        const res = await pywebview.api.extract_sarc_file(
            this.state.selected.path
        );
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.props.showToast(`${this.state.selected.path} extracted`);
    };

    rename_file = async () => {
        const res = await pywebview.api.rename_sarc_file(
            this.state.selected.path,
            this.state.newName
        );
        this.setState({ showRename: false });
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.setState({ sarc: res[0], modded: res[1], modified: true }, () =>
            this.props.showToast(`Rename successful`)
        );
    };

    delete_file = () => {
        const file = this.state.selected.file;
        this.props.showConfirm(
            `Are you sure you want to delete ${file}?`,
            async () => {
                const res = await pywebview.api.delete_sarc_file(
                    this.state.selected.path
                );
                if (res.error) {
                    this.props.onError(res.error);
                    return;
                }
                this.setState(
                    { sarc: res[0], modded: res[1], modified: true },
                    () => this.props.showToast(`Deleted ${file}`)
                );
            }
        );
    };

    replace_file = async () => {
        const file = this.state.selected.file;
        const res = await pywebview.api.replace_sarc_file(
            this.state.selected.path
        );
        if (res.error) {
            if (res.error.msg != "Cancelled") this.props.onError(res.error);
            return;
        }
        this.setState({ sarc: res[0], modded: res[1], modified: true }, () =>
            this.props.showToast(`Replaced ${file}`)
        );
    };

    edit_yaml = async () => {
        const res = await pywebview.api.get_sarc_yaml(this.state.selected.path);
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.props.passFile(res);
    };

    browse_add_file = async () => {
        let file = await pywebview.api.browse();
        if (file) {
            this.setState({ addFile: file });
        }
    };

    handleSelect = async path => {
        if (!this.file_infos.hasOwnProperty(path)) {
            const res = await pywebview.api.get_file_info(path, this.state.be);
            this.setState({ selected: { path, ...res } });
            this.file_infos[path] = res;
        } else {
            this.setState({ selected: { path, ...this.file_infos[path] } });
        }
    };

    render = () => {
        return (
            <>
                <Container fluid className="sarc">
                    <Row className="toolbar">
                        <Col style={{ flexGrow: 0, minWidth: "auto" }}>
                            <ButtonToolbar>
                                <ButtonGroup size="xs" className="mr-2">
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>New</Tooltip>}>
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
                                            <Tooltip>Open a SARC…</Tooltip>
                                        }>
                                        <Button onClick={this.open_sarc}>
                                            <FolderOpen />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Save</Tooltip>}>
                                        <Button
                                            disabled={!this.state.sarc}
                                            onClick={() =>
                                                this.save_sarc(this.state.path)
                                            }>
                                            <Save />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Save As…</Tooltip>}>
                                        <Button
                                            disabled={!this.state.sarc}
                                            onClick={() => this.save_sarc("")}>
                                            <SaveAlt />
                                        </Button>
                                    </OverlayTrigger>
                                </ButtonGroup>
                                <ButtonGroup size="xs">
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Add File…</Tooltip>}>
                                        <Button
                                            disabled={!this.state.sarc}
                                            variant="success"
                                            onClick={() =>
                                                this.setState({ showAdd: true })
                                            }>
                                            <Add />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={
                                            <Tooltip>
                                                Update from Folder…
                                            </Tooltip>
                                        }>
                                        <Button
                                            disabled={!this.state.sarc}
                                            variant="success"
                                            onClick={this.update_folder}>
                                            <FileCopy />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={
                                            <Tooltip>Extract SARC…</Tooltip>
                                        }>
                                        <Button
                                            disabled={!this.state.sarc}
                                            variant="success"
                                            onClick={this.extract_sarc}>
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
                                }}>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={
                                        <Tooltip>{this.state.path}</Tooltip> ||
                                        null
                                    }>
                                    <Badge variant="secondary">
                                        {this.state.path
                                            ? this.state.path
                                                  .replace(/\\/g, "/")
                                                  .split("/")
                                                  .splice(-1)[0]
                                            : this.state.sarc
                                            ? "Unsaved SARC"
                                            : ""}
                                    </Badge>
                                </OverlayTrigger>{" "}
                                {this.state.sarc && (
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
                    <Row className="main">
                        <Col className="tree">
                            {this.state.sarc ? (
                                <>
                                    <TreeView>
                                        {Object.keys(this.state.sarc).map(
                                            file =>
                                                this.render_node(
                                                    file,
                                                    this.state.sarc[file]
                                                )
                                        )}
                                    </TreeView>
                                </>
                            ) : (
                                <div className="nothing">
                                    <span>No SARC open</span>
                                </div>
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
                                            onClick={this.edit_yaml}>
                                            Edit
                                        </Button>
                                    </Col>
                                    <Col>
                                        <Button
                                            variant="warning"
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={this.extract_file}>
                                            Extract
                                        </Button>
                                    </Col>
                                </Row>
                                <Row>
                                    <Col>
                                        <Button
                                            variant="info"
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={() =>
                                                this.setState({
                                                    showRename: true,
                                                    newName:
                                                        this.state.selected.file
                                                })
                                            }>
                                            Rename
                                        </Button>
                                    </Col>
                                    <Col>
                                        <Button
                                            variant="danger"
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={this.delete_file}>
                                            Delete
                                        </Button>
                                    </Col>
                                </Row>
                                <Row>
                                    <Col>
                                        <Button
                                            variant="extra2"
                                            disabled={
                                                !this.state.selected ||
                                                !this.state.selected.file.includes(
                                                    "."
                                                )
                                            }
                                            onClick={this.replace_file}>
                                            Replace
                                        </Button>
                                    </Col>
                                    <Col></Col>
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
                    onHide={() => this.setState({ showRename: false })}>
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
                            onClick={() =>
                                this.setState({ showRename: false })
                            }>
                            Close
                        </Button>
                        <Button variant="primary" onClick={this.rename_file}>
                            Rename
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Modal
                    show={this.state.showNew}
                    onHide={() => this.setState({ showNew: false })}>
                    <Modal.Header closeButton>
                        <Modal.Title>New SARC</Modal.Title>
                    </Modal.Header>
                    <Modal.Body>
                        <p>
                            Select options for new SARC
                        </p>
                        <Form>
                            <Form.Group as={Row}>
                                <Form.Label column sm={3}>
                                    Endianness
                                </Form.Label>
                                <Col sm={9} className="mt-1">
                                    <Form.Check
                                        type="radio"
                                        label="Big endian (Wii U)"
                                        name="new-be"
                                        id="new-be1"
                                        value={true}
                                    />
                                    <Form.Check
                                        type="radio"
                                        label="Little endian (Switch)"
                                        name="new-be"
                                        id="new-be2"
                                        value={false}
                                    />
                                </Col>
                            </Form.Group>
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
                            onClick={() => this.setState({ showNew: false })}>
                            Close
                        </Button>
                        <Button variant="primary" onClick={this.create_sarc}>
                            Create
                        </Button>
                    </Modal.Footer>
                </Modal>
                <Modal
                    show={this.state.showAdd}
                    onHide={() => this.setState({ showAdd: false })}>
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
                                    <InputGroup>
                                        <Form.Control
                                            value={this.state.addFile}
                                            onChange={e =>
                                                this.setState({
                                                    addFile:
                                                        e.currentTarget.value
                                                })
                                            }
                                        />
                                        <InputGroup.Append>
                                            <Button
                                                variant="secondary"
                                                onClick={this.browse_add_file}>
                                                Browse…
                                            </Button>
                                        </InputGroup.Append>
                                    </InputGroup>
                                </Col>
                            </Form.Group>
                            <Form.Group as={Row}>
                                <Form.Label column sm={2}>
                                    Path
                                </Form.Label>
                                <Col sm={10}>
                                    <Form.Control
                                        placeholder="Path/In/Sarc/For.File"
                                        value={this.state.addPath}
                                        onChange={e =>
                                            this.setState({
                                                addPath: e.currentTarget.value
                                            })
                                        }
                                    />
                                </Col>
                            </Form.Group>
                        </Form>
                    </Modal.Body>
                    <Modal.Footer>
                        <Button
                            variant="secondary"
                            onClick={() => this.setState({ showAdd: false })}>
                            Close
                        </Button>
                        <Button variant="primary" onClick={this.add_file}>
                            Add
                        </Button>
                    </Modal.Footer>
                </Modal>
            </>
        );
    };
}

export default SarcEditor;
