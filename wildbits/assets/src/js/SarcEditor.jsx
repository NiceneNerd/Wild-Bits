import React from "react";
import { TreeView, TreeItem } from "@material-ui/lab";
import {
    FolderIcon,
    FolderOpenIcon,
    Archive,
    Unarchive
} from "@material-ui/icons";

const SARC_EXTS = [
    ".sarc",
    ".pack",
    ".bactorpack",
    ".bmodelsh",
    ".beventpack",
    ".stera",
    ".stats",
    ".ssarc",
    ".spack",
    ".sbactorpack",
    ".sbmodelsh",
    ".sbeventpack",
    ".sstera",
    ".sstats",
    ".sblarc",
    ".blarc"
];

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
            if (ext in SARC_EXTS) {
                console.log(file);
                icon = <Archive />;
            } else {
                icon = null;
            }
        }
        return (
            <React.Fragment>
                {icon} {file}
            </React.Fragment>
        );
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
                label={this.render_label(file)}
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
