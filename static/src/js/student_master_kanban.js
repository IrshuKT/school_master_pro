/** @odoo-module **/

import { registry } from "@web/core/registry";
import { kanbanView } from "@web/views/kanban/kanban_view";
import { KanbanController } from "@web/views/kanban/kanban_controller";
import { KanbanRenderer } from "@web/views/kanban/kanban_renderer";
import { useService } from "@web/core/utils/hooks";

class StudentKanbanRenderer extends KanbanRenderer {
    setup() {
        super.setup();
        this.actionService = useService("action");
    }

    // Override empty state rendering
    renderNoContent() {
        const div = document.createElement("div");
        div.classList.add("o_view_nocontent_empty_folder");
        div.innerHTML = `
            <p>No students yet.</p>
            <button class="btn btn-primary">➕ Add Student</button>
        `;
        div.querySelector("button").addEventListener("click", () => {
            this.actionService.doAction("school_master_pro.action_student_master");
        });
        return div;
    }
}

class StudentKanbanController extends KanbanController {
    get Renderer() {
        return StudentKanbanRenderer;
    }
}

registry.category("views").add("student_master_kanban", {
    ...kanbanView,
    Controller: StudentKanbanController,
});
