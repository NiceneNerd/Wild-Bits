import React from "react";
import { TreeView, TreeItem } from "@material-ui/lab";
import {
    FolderIcon,
    FolderOpenIcon,
    Archive,
    Unarchive
} from "@material-ui/icons";

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

    render_label(file) {
        let icon;
        if (!file.includes(".")) {
            icon = <FolderIcon />;
        } else {
            const ext = file.split(".").slice(-1);
        }
    }

    render_node(file, children, path) {
        if (!path) {
            path = [file];
        } else {
            path.push(file);
        }
        return (
            <TreeItem
                key={file}
                nodeId={file}
                label={file}
                path={path.join("/")}
            >
                {Object.keys(children).map(file =>
                    this.render_node(file, children[file], path.slice(0))
                )}
            </TreeItem>
        );
    }

    render() {
        return Object.keys(this.props.sarc) ? (
            <React.Fragment>
                <TreeView>
                    {Object.keys(this.props.sarc).map(file =>
                        this.render_node(file, this.props.sarc[file])
                    )}
                </TreeView>
            </React.Fragment>
        ) : (
            <p>No SARC open</p>
        );
    }
}

export default SarcEditor;
