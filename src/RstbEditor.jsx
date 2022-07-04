import {
    Add,
    Delete,
    Edit,
    FolderOpen,
    ListAlt,
    OpenInNew,
    Save,
    SaveAlt,
    Search
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
import { open, save } from "@tauri-apps/api/dialog";

import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList as List } from "react-window";
import React from "react";
import { invoke } from "@tauri-apps/api/tauri";

const FILTERS = [
    {
        extensions: ["srsizetable", "rsizetable"],
        name: "Resource size table"
    },
    {
        extensions: ["*"],
        name: "All files"
    }
];

class RstbEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rstb: null,
            rstb_files: [],
            modified: false,
            path: "",
            be: false,
            showAdd: false,
            showEdit: false,
            showSearch: false,
            editEntry: "",
            prevSize: 0
        };
        window.openRstb = this.open;
    }

    render_rstb = ({ index, style }) => {
        const file = this.state.rstb_files[index];
        return (
            <Row style={style}>
                <Col
                    className="flex-grow-1"
                    style={{
                        overflowX: "hidden",
                        textOverflow: "ellipsis"
                    }}>
                    {isNaN(file)
                        ? file
                        : `Unknown file 0x${parseInt(file).toString(16)}`}
                </Col>
                <Col className="flex-grow-0" style={{ whiteSpace: "nowrap" }}>
                    {this.state.rstb[file]} bytes
                </Col>
                <Col className="flex-grow-0">
                    <ButtonGroup size="xs">
                        <OverlayTrigger overlay={<Tooltip>Edit</Tooltip>}>
                            <Button
                                variant="success"
                                onClick={() =>
                                    this.setState({
                                        showEdit: true,
                                        editEntry: file,
                                        prevSize: this.state.rstb[file]
                                    })
                                }>
                                <Edit />
                            </Button>
                        </OverlayTrigger>
                        <OverlayTrigger overlay={<Tooltip>Delete</Tooltip>}>
                            <Button
                                variant="danger"
                                onClick={() => this.delete_entry(file)}>
                                <Delete />
                            </Button>
                        </OverlayTrigger>
                    </ButtonGroup>
                </Col>
            </Row>
        );
    };

    search = query => {
        this.setState({ showSearch: false }, async () => {
            const hash = await invoke("add_name", { name: query });
            const idx = this.state.rstb_files.indexOf(hash.toString());
            if (idx > -1) {
                this.state.rstb_files[idx] = query;
                this.state.rstb[query] = this.state.rstb[hash];
                delete this.state.rstb[hash];
            }
            this.setState(
                {
                    rstb: this.state.rstb,
                    rstb_files: this.state.rstb_files
                },
                () => {
                    document.getElementById("rstb-filter").value = query;
                    this.update_filter();
                }
            );
        });
    };

    update_filter = () => {
        const filter = document.getElementById("rstb-filter").value;
        this.setState({ rstb_files: [] }, () => {
            this.setState({
                rstb_files: Object.keys(this.state.rstb)
                    .filter(key => key.includes(filter))
                    .sort(file_sort)
            });
        });
    };

    open = data => {
        const rstb_files = Object.keys(data.rstb).sort(file_sort);
        window.files = rstb_files;
        this.setState({ ...data, rstb_files: [], modified: false }, () =>
            this.setState({ rstb_files })
        );
    };

    open_rstb = async () => {
        const file = await open({
            filters: FILTERS
        });
        if (!file) return;
        this.props.setLoading(true);
        try {
            const data = await invoke("open_rstb", { file });
            this.open(data);
        } catch (err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    save_rstb = async file => {
        if (!file) {
            file = await save({
                filters: FILTERS
            });
            if (!file) return;
        }
        this.props.setLoading(true);
        try {
            await invoke("save_rstb", { file });
            this.props.showToast("File saved");
            const rstb_files = this.state.rstb_files;
            this.setState({ path: file, rstb_files: [], modified: false }, () =>
                this.setState({ rstb_files })
            );
        } catch (err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    add_entry = (path, size) => {
        size = parseInt(size);
        this.setState({ showAdd: false }, async () => {
            try {
                await invoke("set_size", { path, size });
            } catch (err) {
                this.props.onError(err);
                return;
            }
            const rstb_files = this.state.rstb_files;
            rstb_files.push(path);
            const rstb = this.state.rstb;
            rstb[path] = size;
            this.setState({ rstb_files, rstb, modified: true }, () =>
                this.props.showToast("RSTB entry added")
            );
        });
    };

    edit_entry = size => {
        size = parseInt(size);
        this.setState({ showEdit: false }, async () => {
            try {
                await invoke("set_size", { path: this.state.editEntry, size });
            } catch (err) {
                this.props.onError(err);
                return;
            }
            const rstb = this.state.rstb;
            rstb[this.state.editEntry] = size;
            const rstb_files = this.state.rstb_files;
            this.setState(
                {
                    rstb,
                    rstb_files: [],
                    modified: true,
                    editEntry: ""
                },
                () => {
                    this.props.showToast("RSTB entry updated");
                    this.setState({ rstb_files });
                }
            );
        });
    };

    delete_entry = path => {
        this.props.showConfirm(
            `Are you sure you want to delete the RSTB entry for <code>${path}</code>?`,
            async () => {
                try {
                    await invoke("delete_entry", { path });
                } catch (err) {
                    this.props.onError(err);
                }
                const rstb = this.state.rstb;
                delete rstb[path];
                const rstb_files = this.state.rstb_files.filter(f => f != path);
                this.setState({ rstb, rstb_files, modified: true }, () =>
                    this.props.showToast("RSTB entry deleted")
                );
            }
        );
    };

    scan_mod = async () => {
        const folder = await open({ directory: true });
        if (!folder) return;
        this.props.setLoading(true);
        try {
            await invoke("scan_mod", { path: folder });
            this.props.showToast("Added mod files to name table");
        } catch (err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    export_rstb = async () => {
        const file = await save({
            filters: [
                {
                    extensions: ["json"],
                    name: "JSON File"
                },
                {
                    extensions: ["*"],
                    name: "All Files"
                }
            ]
        });
        if (!file) return;
        this.props.setLoading(true);
        try {
            await invoke("export_rstb", { file });
            this.props.showToast("RSTB exported");
        } catch (err) {
            this.props.onError(err);
        }
        this.props.setLoading(false);
    };

    render = () => {
        return (
            <>
                <Container fluid className="rstb">
                    <Row className="toolbar">
                        <Col style={{ flexGrow: 0, minWidth: "auto" }}>
                            <ButtonToolbar>
                                <ButtonGroup size="xs" className="mr-2">
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={
                                            <Tooltip>Open RSTB File…</Tooltip>
                                        }>
                                        <Button onClick={this.open_rstb}>
                                            <FolderOpen />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Save</Tooltip>}>
                                        <Button
                                            onClick={() =>
                                                this.save_rstb(this.state.path)
                                            }
                                            disabled={!this.state.rstb}>
                                            <Save />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        placement="bottom"
                                        overlay={<Tooltip>Save As…</Tooltip>}>
                                        <Button
                                            onClick={() => this.save_rstb("")}
                                            disabled={!this.state.rstb}>
                                            <SaveAlt />
                                        </Button>
                                    </OverlayTrigger>
                                </ButtonGroup>
                                <ButtonGroup size="xs">
                                    <OverlayTrigger
                                        overlay={<Tooltip>Add Entry…</Tooltip>}
                                        placement="bottom">
                                        <Button
                                            variant="success"
                                            disabled={!this.state.rstb}
                                            onClick={() =>
                                                this.setState({ showAdd: true })
                                            }>
                                            <Add />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        overlay={
                                            <Tooltip>
                                                Search for Unknown Entry…
                                            </Tooltip>
                                        }
                                        placement="bottom">
                                        <Button
                                            variant="success"
                                            disabled={!this.state.rstb}
                                            onClick={() =>
                                                this.setState({
                                                    showSearch: true
                                                })
                                            }>
                                            <Search />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        overlay={
                                            <Tooltip>
                                                Scan Mod for Resource Names…
                                            </Tooltip>
                                        }
                                        placement="bottom">
                                        <Button
                                            variant="success"
                                            disabled={!this.state.rstb}
                                            onClick={this.scan_mod}>
                                            <ListAlt />
                                        </Button>
                                    </OverlayTrigger>
                                    <OverlayTrigger
                                        overlay={
                                            <Tooltip>Export as JSON</Tooltip>
                                        }
                                        placement="bottom">
                                        <Button
                                            variant="success"
                                            disabled={!this.state.rstb}
                                            onClick={this.export_rstb}>
                                            <OpenInNew />
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
                                            : this.state.rstb
                                            ? "Unsaved RSTB"
                                            : ""}
                                    </Badge>
                                </OverlayTrigger>{" "}
                                {this.state.rstb && (
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
                    <div className="main">
                        {this.state.rstb && (
                            <>
                                <Row className="flex-grow-1">
                                    <AutoSizer>
                                        {({ height, width }) => (
                                            <List
                                                height={height}
                                                itemCount={
                                                    Object.keys(
                                                        this.state.rstb_files
                                                    ).length
                                                }
                                                itemSize={32}
                                                width={width}
                                                className="rstb-list">
                                                {this.render_rstb}
                                            </List>
                                        )}
                                    </AutoSizer>
                                </Row>
                                <Row className="flex-grow-0 m-1 bg-dark">
                                    <InputGroup>
                                        <FormControl
                                            placeholder="Filter RSTB entries"
                                            id="rstb-filter"
                                            onKeyUp={event =>
                                                event.keyCode == 13 &&
                                                this.update_filter()
                                            }
                                        />
                                        <InputGroup.Append>
                                            <Button
                                                variant="secondary"
                                                onClick={this.update_filter}>
                                                Search
                                            </Button>
                                        </InputGroup.Append>
                                    </InputGroup>
                                </Row>
                            </>
                        )}
                    </div>
                </Container>
                <AddRstbModal
                    show={this.state.showAdd}
                    onClose={() => this.setState({ showAdd: false })}
                    onError={this.props.onError}
                    onAdd={this.add_entry}
                />
                <EditRstbModal
                    show={this.state.showEdit}
                    prevSize={this.state.prevSize}
                    entry={this.state.editEntry}
                    onClose={() => this.setState({ showEdit: false })}
                    onError={this.props.onError}
                    onSet={this.edit_entry}
                />
                <SearchModal
                    show={this.state.showSearch}
                    onClose={() => this.setState({ showSearch: false })}
                    onSearch={this.search}
                />
            </>
        );
    };
}

class SearchModal extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            query: ""
        };
    }
    render() {
        return (
            <Modal show={this.props.show} onHide={this.props.onClose}>
                <Modal.Header closeButton>
                    <Modal.Title>Search for RSTB Entry</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p>
                        Enter the resource path of the file you want to search
                        for.
                    </p>
                    <Form>
                        <Form.Group as={Row}>
                            <Form.Label column sm={2}>
                                File
                            </Form.Label>
                            <Col sm={10}>
                                <Form.Control
                                    placeholder="Canonical path to file"
                                    value={this.state.query}
                                    onChange={e =>
                                        this.setState({
                                            query: e.currentTarget.value
                                        })
                                    }
                                />
                            </Col>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={this.props.onClose}>
                        Close
                    </Button>
                    <Button
                        variant="primary"
                        onClick={() => this.props.onSearch(this.state.query)}>
                        OK
                    </Button>
                </Modal.Footer>
            </Modal>
        );
    }
}

class AddRstbModal extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            addPath: "",
            addSize: 0
        };
        this.browse = this.browse.bind(this);
    }

    async browse() {
        const file = await open();
        if (!file) return;
        try {
            const size = await invoke("calc_size", { file });
            this.setState({ addSize: size });
        } catch (err) {
            this.props.onError(err);
        }
    }

    render() {
        return (
            <Modal show={this.props.show} onHide={this.props.onClose}>
                <Modal.Header>
                    <Modal.Title>Add RSTB Entry</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p>
                        Enter the{" "}
                        <a href="https://zeldamods.org/wiki/Canonical_resource_path">
                            canonical resource path
                        </a>{" "}
                        for the RSTB entry you want to add, and then enter the
                        resource size. You can also detect the resource size by
                        selecting the file you want to add to the RSTB.
                    </p>
                    <Form>
                        <Form.Group as={Row}>
                            <Form.Label column sm={2}>
                                Path
                            </Form.Label>
                            <Col sm={10}>
                                <Form.Control
                                    placeholder="Canonical path to file"
                                    value={this.state.addPath}
                                    onChange={e =>
                                        this.setState({
                                            addPath: e.currentTarget.value
                                        })
                                    }
                                />
                            </Col>
                        </Form.Group>
                        <Form.Group as={Row}>
                            <Form.Label column sm={2}>
                                Size
                            </Form.Label>
                            <Col sm={10}>
                                <InputGroup>
                                    <Form.Control
                                        value={this.state.addSize}
                                        type="number"
                                        onChange={e =>
                                            this.setState({
                                                addSize: e.currentTarget.value
                                            })
                                        }
                                    />
                                    <InputGroup.Append>
                                        <Button
                                            variant="secondary"
                                            onClick={this.browse}>
                                            Browse…
                                        </Button>
                                    </InputGroup.Append>
                                </InputGroup>
                            </Col>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={this.props.onClose}>
                        Close
                    </Button>
                    <Button
                        variant="primary"
                        onClick={() =>
                            this.props.onAdd(
                                this.state.addPath,
                                this.state.addSize
                            )
                        }>
                        OK
                    </Button>
                </Modal.Footer>
            </Modal>
        );
    }
}

class EditRstbModal extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            size: 0
        };
        this.browse = this.browse.bind(this);
    }

    componentDidUpdate(prevProps) {
        if (!prevProps.show && this.props.show) {
            this.setState({
                size: this.props.prevSize
            });
        }
    }

    async browse() {
        const file = await open();
        if (!file) return;
        try {
            const size = await invoke("calc_size", { file });
            this.setState({ addSize: size });
        } catch (err) {
            this.props.onError(err);
        }
    }

    render() {
        return (
            <Modal show={this.props.show} onHide={this.props.onClose}>
                <Modal.Header>
                    <Modal.Title>Edit RSTB Entry</Modal.Title>
                </Modal.Header>
                <Modal.Body>
                    <p>
                        Enter the new resource size for{" "}
                        <code>{this.props.entry}</code>. You can also detect the
                        resource size by selecting the file you want to add to
                        the RSTB.
                    </p>
                    <Form>
                        <Form.Group as={Row}>
                            <Form.Label column sm={2}>
                                Size
                            </Form.Label>
                            <Col sm={10}>
                                <InputGroup>
                                    <Form.Control
                                        value={this.state.size}
                                        type="number"
                                        onChange={e =>
                                            this.setState({
                                                size: e.currentTarget.value
                                            })
                                        }
                                    />
                                    <InputGroup.Append>
                                        <Button
                                            variant="secondary"
                                            onClick={this.browse}>
                                            Browse…
                                        </Button>
                                    </InputGroup.Append>
                                </InputGroup>
                            </Col>
                        </Form.Group>
                    </Form>
                </Modal.Body>
                <Modal.Footer>
                    <Button variant="secondary" onClick={this.props.onClose}>
                        Close
                    </Button>
                    <Button
                        variant="primary"
                        onClick={() => this.props.onSet(this.state.size)}>
                        OK
                    </Button>
                </Modal.Footer>
            </Modal>
        );
    }
}

function file_sort(a, b) {
    if (isNaN(a) && isNaN(b)) {
        return a.localeCompare(b);
    } else if (!isNaN(a) && !isNaN(b)) {
        return parseInt(a) - parseInt(b);
    } else if (isNaN(a) && !isNaN(b)) {
        return -1;
    } else {
        return 1;
    }
}

export default RstbEditor;
