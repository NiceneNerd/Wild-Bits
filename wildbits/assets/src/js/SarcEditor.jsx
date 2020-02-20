import React from "react";
import ListGroup from "react-bootstrap/ListGroup";
import { TreeView, TreeItem } from "@material-ui/lab";

class SarcEditor extends React.Component {
    constructor(props) {
        super(props);
        this.state = {
            show_menu: false,
            menu_x: 0,
            menu_y: 0,
            menu_file: ""
        };
    }

    render_sarc(sarc) {
        return (
            <TreeItem key={sarc.name} nodeId={sarc.name} label={sarc.name}>
                {sarc.files.map(file =>
                    file.files ? this.render_sarc(file) : null
                )}
            </TreeItem>
        );
    }

    render() {
        return this.props.sarc.files ? (
            <React.Fragment>
                <TreeView>
                    {this.props.sarc.files.map(file => this.render_sarc(file))}
                </TreeView>
            </React.Fragment>
        ) : (
            <p>No SARC open</p>
        );
    }
}

export default SarcEditor;
