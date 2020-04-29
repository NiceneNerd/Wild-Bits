import React from "react";
import {
    Badge,
    Container,
    Row,
    Col,
    Button,
    ButtonGroup,
    ButtonToolbar,
    OverlayTrigger,
    Table,
    Tooltip,
    InputGroup,
    FormControl
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
    SaveAlt
} from "@material-ui/icons";
import AutoSizer from "react-virtualized-auto-sizer";
import { FixedSizeList as List } from "react-window";

class RstbEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            rstb: null,
            modified: false,
            path: "",
            be: false
        }
        this.open_rstb = this.open_rstb.bind(this);
        this.save_rstb = this.save_rstb.bind(this);
        this.render_rstb = this.render_rstb.bind(this);
    }

    render_rstb({index, style}) {
        const file = Object.keys(this.state.rstb)[index];
        return (
            <Row style={style}>
                <Col className="flex-grow-1" style={{overflowX: 'hidden', textOverflow: 'ellipsis'}}>
                    {isNaN(file)
                        ? file
                        : `Unknown file 0x${parseInt(file).toString(16)}`
                    }
                </Col>
                <Col className="flex-grow-0" style={{whiteSpace: 'nowrap'}}>{this.state.rstb[file]} bytes</Col>
                <Col className="flex-grow-0">
                    <ButtonGroup size="xs">
                        <Button variant="success">
                            <Edit />
                        </Button>
                        <Button variant="danger">
                            <Delete />
                        </Button>
                    </ButtonGroup>
                </Col>
            </Row>
        );
    }

    open_rstb() {
        pywebview.api.open_rstb().then(res => {
            if (res.error) {
                this.props.onError(res.error);
                return;
            }
            this.setState({ ...res, modified: false });
        });
    }

    save_rstb() {

    }

    render() {
        return (
            <Container fluid className="rstb">
                <Row className="toolbar">
                    <Col style={{ flexGrow: 0, minWidth: "fit-content" }}>
                        <ButtonToolbar>
                            <ButtonGroup size="xs" className="mr-2">
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={
                                        <Tooltip>Open RSTB File...</Tooltip>
                                    }
                                >
                                    <Button onClick={this.open_rstb}>
                                        <FolderOpen />
                                    </Button>
                                </OverlayTrigger>
                                <OverlayTrigger
                                    placement="bottom"
                                    overlay={<Tooltip>Save</Tooltip>}
                                >
                                    <Button
                                        onClick={() =>
                                            this.save_rstb(this.state.path)
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
                                        onClick={() => this.save_rstb("")}
                                    >
                                        <SaveAlt />
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
                                    : this.state.rstb
                                    ? "Unsaved RSTB"
                                    : ""}
                            </Badge>{" "}
                            {this.state.rstb && (
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
                <div className="main">
                    {this.state.rstb && (
                        <>
                            {/* <Row className="flex-grow-0">
                                <Col sm={8}>
                                    <div>File</div>
                                </Col>
                                <Col sm={2}>
                                    <div>Size</div>
                                </Col>
                                <Col sm={2}>
                                    <div>Actions</div>
                                </Col>
                            </Row> */}
                            <Row className="flex-grow-1">
                                <AutoSizer>
                                    {({height, width}) => (
                                        <List
                                            height={height}
                                            itemCount={Object.keys(this.state.rstb).length}
                                            itemSize={32}
                                            width={width}>
                                            {this.render_rstb}
                                        </List>
                                    )}
                                </AutoSizer>
                            </Row>
                            <Row className="flex-grow-0">
                                <InputGroup>
                                    <FormControl placeholder="Filter RSTB entries" />
                                    <InputGroup.Append>
                                        <Button variant="secondary">Search</Button>
                                    </InputGroup.Append>
                                </InputGroup>
                            </Row>
                        </>
                    )}
                </div>
            </Container>
        )
    }
}

export default RstbEditor;
