import React from "react";
import { TreeView, TreeItem } from "@material-ui/lab";
import { Folder, FolderOpen, Archive, Unarchive } from "@material-ui/icons";

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
    "blarc"
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
            icon = <Folder fontSize="small" />;
        } else {
            const ext = file.split(".").slice(-1)[0];
            if (SARC_EXTS.includes(ext)) {
                icon = <Archive fontSize="small" />;
            } else {
                icon = null;
            }
        }
        return (
            <React.Fragment>
                {icon} <span style={{ verticalAlign: "text-top" }}>{file}</span>
            </React.Fragment>
        );
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
        return (
            <TreeItem
                key={file}
                nodeId={file}
                expandIcon={
                    type == "folder" ? (
                        <Folder fontSize="small" />
                    ) : type == "sarc" ? (
                        <Unarchive fontSize="small" />
                    ) : null
                }
                collapseIcon={
                    type == "folder" ? (
                        <FolderOpen fontSize="small" />
                    ) : type == "sarc" ? (
                        <Archive fontSize="small" />
                    ) : null
                }
                label={
                    <span style={{ verticalAlign: "text-top" }}>{file}</span>
                }
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
