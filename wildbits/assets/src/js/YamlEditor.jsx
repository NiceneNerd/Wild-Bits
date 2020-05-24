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
import {
    Assignment,
    FolderOpen,
    Save,
    SaveAlt,
    Search,
    FindReplace,
    Undo,
    Redo,
    FileCopy,
    ControlCamera
} from "@material-ui/icons";
import CutIcon from "./CutIcon.jsx";
import AceEditor from "react-ace";
import "ace-builds/src-min-noconflict/ext-searchbox";
import "ace-builds/src-noconflict/mode-yaml";
import "ace-builds/src-noconflict/ext-language_tools";
import "ace-builds/src-noconflict/theme-monokai";

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
        this.save_yaml = this.save_yaml.bind(this);
        this.open_sarc_yaml = this.open_sarc_yaml.bind(this);
        this.aceRef = React.createRef();
    }

    open_sarc_yaml = res => {
        this.setState({ ...res, modified: false });
    };

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

    save_yaml(path) {
        pywebview.api
            .save_yaml(this.state.yaml, this.state.type, this.state.be, path)
            .then(res => {
                console.log(res);
                if (res.error) {
                    this.props.onError(res.error);
                    return;
                }
                this.props.showToast(
                    "File saved" + path.startsWith("SARC:") ? " to SARC" : ""
                );
                if (path.startsWith("SARC:")) {
                    this.props.passMod(path.replace("SARC:", ""));
                }
            }).catch(
            err => this.props.onError(err)
        );
    }

    render() {
        return (
            <Container
                fluid
                className="yaml d-flex flex-column"
                style={{ height: "100%" }}>
                <Row className="toolbar">
                    <Col style={{ flexGrow: 0, minWidth: "auto" }}>
                        <ButtonToolbar>
                            <ButtonGroup size="xs" className="mr-2">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Open File…</Tooltip>}>
                                    <Button onClick={this.open_yaml}>
                                        <FolderOpen />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Save</Tooltip>}>
                                    <Button
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.save_yaml(this.state.path)
                                        }>
                                        <Save />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Save As…</Tooltip>}>
                                    <Button
                                        disabled={!this.state.yaml}
                                        onClick={() => this.save_yaml("")}>
                                        <SaveAlt />
                                    </Button>
                                </OverlayTrigger>
                            </ButtonGroup>
                            <ButtonGroup size="xs" className="mr-2">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Cut</Tooltip>}>
                                    <Button
                                        variant="success"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "cut"
                                            )
                                        }>
                                        <CutIcon />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Copy</Tooltip>}>
                                    <Button
                                        variant="success"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "copy"
                                            )
                                        }>
                                        <FileCopy />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Paste</Tooltip>}>
                                    <Button
                                        variant="success"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "paste"
                                            )
                                        }>
                                        <Assignment />
                                    </Button>
                                </OverlayTrigger>
                            </ButtonGroup>
                            <ButtonGroup size="xs">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Undo</Tooltip>}>
                                    <Button
                                        variant="secondary"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "undo"
                                            )
                                        }>
                                        <Undo />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Redo</Tooltip>}>
                                    <Button
                                        variant="secondary"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "redo"
                                            )
                                        }>
                                        <Redo />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Find</Tooltip>}>
                                    <Button
                                        variant="secondary"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "find"
                                            )
                                        }>
                                        <Search />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={
                                        <Tooltip>Find and Replace</Tooltip>
                                    }>
                                    <Button
                                        variant="secondary"
                                        disabled={!this.state.yaml}
                                        onClick={() =>
                                            this.aceRef.current.editor.execCommand(
                                                "replace"
                                            )
                                        }>
                                        <FindReplace />
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
                                    <Tooltip>{this.state.path}</Tooltip> || null
                                }>
                                <Badge variant="secondary">
                                    {this.state.path
                                        ? this.state.path
                                              .replace(/\\/g, "/")
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
                <Row className="d-flex flex-column flex-grow-1">
                    <AceEditor
                        ref={this.aceRef}
                        className="flex-grow-1 ace-material"
                        mode="yaml"
                        theme="monokai"
                        style={{ width: "calc(100% - 7px)" }}
                        fontSize={14}
                        showPrintMargin={false}
                        enableLiveAutocompletion={true}
                        value={this.state.yaml}
                        onChange={yaml =>
                            this.setState({ yaml, modified: true })
                        }
                    />
                </Row>
            </Container>
        );
    }
}

export default YamlEditor;
