import React from "react";
import {
    Badge,
    Container,
    Form,
    Row,
    Col,
    Button,
    ButtonGroup,
    ButtonToolbar,
    OverlayTrigger,
    Table,
    Tooltip,
    InputGroup,
    FormControl,
    Modal
} from "react-bootstrap";
import {
    Add,
    Edit,
    Delete,
    Create,
    FileCopy,
    Folder,
    FolderOpen,
    Archive,
    Unarchive,
    Save,
    SaveAlt,
    OpenInNew
} from "@material-ui/icons";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList as List } from "react-window";

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
            editEntry: ""
        };
        this.open_rstb = this.open_rstb.bind(this);
        this.save_rstb = this.save_rstb.bind(this);
        this.render_rstb = this.render_rstb.bind(this);
        this.update_filter = this.update_filter.bind(this);
        this.add_entry = this.add_entry.bind(this);
        this.edit_entry = this.edit_entry.bind(this);
        this.export_rstb = this.export_rstb.bind(this);
    }

    render_rstb({ index, style }) {
        const file = this.state.rstb_files[index];
        return (
            <Row style={style}>
                <Col
                    className="flex-grow-1"
                    style={{ overflowX: "hidden", textOverflow: "ellipsis" }}>
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
                                        editEntry: file
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
    }

    update_filter() {
        const filter = document.getElementById("rstb-filter").value;
        this.setState({
            rstb_files: Object.keys(this.state.rstb)
                .filter(key => key.includes(filter))
                .sort(file_sort)
        });
    }

    open_rstb() {
        pywebview.api.open_rstb().then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
            const rstb_files = Object.keys(res.rstb).sort(file_sort);
            this.setState({ ...res, rstb_files: [], modified: false }, () =>
                this.setState({ rstb_files })
            );
        });
    }

    save_rstb(path) {
        pywebview.api.save_rstb(path).then(res => {
            if (res.error && res.error != "Cancelled") {
                this.props.onError(res.error);
                return;
            }
            const rstb_files = this.state.rstb_files;
            this.setState(
                { path: res.path, rstb_files: [], modified: false },
                () => this.setState({ rstb_files })
            );
        });
    }

    add_entry(path, size) {
        size = parseInt(size);
        this.setState({ showAdd: false }, () => {
            pywebview.api.set_entry(path, size).then(res => {
                if (res.error) {
                    this.props.onError(res.error);
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
        });
    }

    edit_entry(size) {
        size = parseInt(size);
        this.setState({ showEdit: false }, () => {
            pywebview.api.set_entry(this.state.editEntry, size).then(res => {
                if (res.error) {
                    this.props.onError(res.error);
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
        });
    }

    delete_entry(file) {
        this.props.showConfirm(
            `Are you sure you want to delete the RSTB entry for <code>${file}</code>?`,
            () => {
                pywebview.api.delete_entry(file).then(() => {
                    const rstb = this.state.rstb;
                    delete rstb[file];
                    const rstb_files = this.state.rstb_files.filter(
                        f => f != file
                    );
                    this.setState({ rstb, rstb_files, modified: true }, () =>
                        this.props.showToast("RSTB entry deleted")
                    );
                });
            }
        );
    }

    export_rstb() {
        pywebview.api.export_rstb().then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
            this.props.showToast("RSTB exported");
        });
    }

    render() {
        return (
            <>
                <Container fluid className="rstb">
                    <Row className="toolbar">
                        <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
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
                                                  .replace("\\", "/")
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
                    entry={this.state.editEntry}
                    onClose={() => this.setState({ showEdit: false })}
                    onError={this.props.onError}
                    onSet={this.edit_entry}
                />
            </>
        );
    }
}

class AddRstbModal extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            addPath: "",
            addSize: 0,
            guessed: false
        };
        this.browse = this.browse.bind(this);
    }

    async browse() {
        let res = await pywebview.api.browse_file_size();
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.setState({ addSize: res.size, guessed: res.guess });
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
                                        className={
                                            this.state.guessed
                                                ? "bg-warning"
                                                : ""
                                        }
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
            size: 0,
            guessed: false
        };
        this.browse = this.browse.bind(this);
    }

    async browse() {
        let res = await pywebview.api.browse_file_size();
        if (res.error) {
            this.props.onError(res.error);
            return;
        }
        this.setState({ size: res.size, guessed: res.guess });
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
                                        className={
                                            this.state.guessed
                                                ? "bg-warning"
                                                : ""
                                        }
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
