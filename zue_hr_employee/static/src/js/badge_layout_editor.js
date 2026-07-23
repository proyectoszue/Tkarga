/** @odoo-module **/

import { Component, useState, onWillUpdateProps } from "@odoo/owl";
import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";

const PX_PER_CM = 50;
const ELEMENTS = [
    { key: "photo", label: "Foto" },
    { key: "name", label: "Nombre" },
    { key: "job", label: "Cargo" },
    { key: "vat", label: "Documento" },
    { key: "rh", label: "RH" },
    { key: "date", label: "Fecha" },
    { key: "area", label: "Área" },
];
const TEXT_DEFAULTS = { font_size: 5.5, color: "#000000" };

const DEFAULT_VERTICAL = {
    photo: { top: 3.07, left: 0.49, width: 1.82, height: 2.74 },
    name: { top: 3.45, left: 2.45, width: 2.75, height: 0.7, ...TEXT_DEFAULTS },
    job: { top: 4.5, left: 2.45, width: 2.75, height: 0.55, ...TEXT_DEFAULTS },
    vat: { top: 5.45, left: 2.85, width: 2.35, height: 0.35, ...TEXT_DEFAULTS },
    rh: { top: 6.15, left: 1.6, width: 1.2, height: 0.28, ...TEXT_DEFAULTS },
    date: { top: 6.75, left: 2.6, width: 2.0, height: 0.28, ...TEXT_DEFAULTS },
    area: { top: 7.9, left: 0.4, width: 4.7, height: 0.4, ...TEXT_DEFAULTS },
};

const DEFAULT_HORIZONTAL = {
    photo: { top: 2.4, left: 0.55, width: 2.9, height: 2.9 },
    name: { top: 2.5, left: 3.8, width: 6.4, height: 0.8, ...TEXT_DEFAULTS },
    job: { top: 3.4, left: 3.8, width: 6.4, height: 0.55, ...TEXT_DEFAULTS },
    vat: { top: 4.0, left: 3.8, width: 6.4, height: 0.4, ...TEXT_DEFAULTS },
    rh: { top: 4.55, left: 3.8, width: 2.5, height: 0.35, ...TEXT_DEFAULTS },
    date: { top: 4.55, left: 6.5, width: 3.5, height: 0.35, ...TEXT_DEFAULTS },
    area: { top: 5.2, left: 3.8, width: 6.4, height: 0.4, ...TEXT_DEFAULTS },
};

function parseLayout(raw, orientation) {
    const defaults = orientation === "vertical" ? DEFAULT_VERTICAL : DEFAULT_HORIZONTAL;
    let saved = {};
    try {
        saved = JSON.parse(raw || "{}") || {};
    } catch {
        saved = {};
    }
    const layout = {};
    for (const [key, defBox] of Object.entries(defaults)) {
        const box = { ...defBox };
        if (saved[key] && typeof saved[key] === "object") {
            for (const attr of ["top", "left", "width", "height", "font_size"]) {
                const val = Number(saved[key][attr]);
                if (!Number.isNaN(val)) {
                    box[attr] = val;
                }
            }
            if (saved[key].color) {
                box.color = saved[key].color;
            }
        }
        layout[key] = box;
    }
    return layout;
}

export class BadgeLayoutEditor extends Component {
    static template = "zue_hr_employee.BadgeLayoutEditor";
    static props = { ...standardFieldProps };

    setup() {
        this.elements = ELEMENTS;
        this.state = useState({
            layout: parseLayout(this.props.record.data.z_layout_json, this.props.record.data.orientation),
            activeKey: null,
        });
        this.drag = null;

        onWillUpdateProps((nextProps) => {
            const nextRaw = nextProps.record.data.z_layout_json;
            const nextOrientation = nextProps.record.data.orientation;
            if (
                nextRaw !== this.props.record.data.z_layout_json ||
                nextOrientation !== this.props.record.data.orientation
            ) {
                this.state.layout = parseLayout(nextRaw, nextOrientation);
            }
        });
    }

    get orientation() {
        return this.props.record.data.orientation || "horizontal";
    }

    get cardWidthCm() {
        return this.orientation === "vertical" ? 5.5 : 10.8;
    }

    get cardHeightCm() {
        return this.orientation === "vertical" ? 8.6 : 7.0;
    }

    get canvasStyle() {
        return `width:${this.cardWidthCm * PX_PER_CM}px;height:${this.cardHeightCm * PX_PER_CM}px;`;
    }

    get backgroundUrl() {
        const record = this.props.record;
        if (record.resId && record.data.img_header_file) {
            return `/web/image?model=report.print.badge.template&id=${record.resId}&field=img_header_file&unique=${record.data.img_header_file}`;
        }
        if (record.data.img_header_file) {
            return `data:image/png;base64,${record.data.img_header_file}`;
        }
        return "";
    }

    get activeLabel() {
        const found = this.elements.find((e) => e.key === this.state.activeKey);
        return found ? found.label : "";
    }

    get isTextElement() {
        return this.state.activeKey && this.state.activeKey !== "photo";
    }

    boxStyle(key) {
        const box = this.state.layout[key];
        return (
            `top:${box.top * PX_PER_CM}px;left:${box.left * PX_PER_CM}px;` +
            `width:${box.width * PX_PER_CM}px;height:${box.height * PX_PER_CM}px;`
        );
    }

    selectElement(key) {
        this.state.activeKey = key;
    }

    onPointerDown(ev, key) {
        if (this.props.readonly) {
            return;
        }
        ev.preventDefault();
        this.state.activeKey = key;
        this.drag = {
            key,
            startX: ev.clientX,
            startY: ev.clientY,
            originTop: this.state.layout[key].top,
            originLeft: this.state.layout[key].left,
        };
        window.addEventListener("pointermove", this.onPointerMove);
        window.addEventListener("pointerup", this.onPointerUp);
    }

    onPointerMove = (ev) => {
        if (!this.drag) {
            return;
        }
        const key = this.drag.key;
        const dxCm = (ev.clientX - this.drag.startX) / PX_PER_CM;
        const dyCm = (ev.clientY - this.drag.startY) / PX_PER_CM;
        let left = this.drag.originLeft + dxCm;
        let top = this.drag.originTop + dyCm;
        const box = this.state.layout[key];
        left = Math.max(0, Math.min(left, this.cardWidthCm - box.width));
        top = Math.max(0, Math.min(top, this.cardHeightCm - box.height));
        this.state.layout[key] = { ...box, top: Number(top.toFixed(2)), left: Number(left.toFixed(2)) };
    };

    onPointerUp = async () => {
        if (!this.drag) {
            return;
        }
        this.drag = null;
        window.removeEventListener("pointermove", this.onPointerMove);
        window.removeEventListener("pointerup", this.onPointerUp);
        await this.persistLayout();
    };

    async persistLayout() {
        const value = JSON.stringify(this.state.layout);
        await this.props.record.update({ z_layout_json: value });
    }

    async onSizeChange(key, attr, ev) {
        if (this.props.readonly) {
            return;
        }
        const val = Number(ev.target.value);
        if (Number.isNaN(val) || val <= 0) {
            return;
        }
        this.state.layout[key] = {
            ...this.state.layout[key],
            [attr]: Number(val.toFixed(2)),
        };
        this.state.activeKey = key;
        await this.persistLayout();
    }

    async onColorChange(key, ev) {
        if (this.props.readonly) {
            return;
        }
        const color = ev.target.value || "#000000";
        this.state.layout[key] = {
            ...this.state.layout[key],
            color,
        };
        this.state.activeKey = key;
        await this.persistLayout();
    }

    async resetLayout() {
        if (this.props.readonly) {
            return;
        }
        const defaults = this.orientation === "vertical" ? DEFAULT_VERTICAL : DEFAULT_HORIZONTAL;
        this.state.layout = JSON.parse(JSON.stringify(defaults));
        await this.persistLayout();
    }
}

export const badgeLayoutEditor = {
    component: BadgeLayoutEditor,
    supportedTypes: ["text", "char"],
};

registry.category("fields").add("z_badge_layout_editor", badgeLayoutEditor);
