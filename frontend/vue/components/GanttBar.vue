<template>
    <div :class="{ 'gantt-bar': true, 'dragging': dragging }" ref="ganttBar">
        <template v-if="data.status == 2">
            <gantt-maintenance-bar
                :assignment="data"
                :start-date="startDate"
                :timezone="timezone"
                :unit="unit"
                :selected="selected && !assigned"
                :dragging="dragging"
                :drag-offset="internalDragOffset"
                :editing="editing"
                :writable="writable"
                @resized="handleResizeBar">
            </gantt-maintenance-bar>
        </template>
        <template v-else-if="data.status == 3">
            <gantt-unscheduled-flight-bar
                :flight="data"
                :start-date="startDate"
                :timezone="timezone"
                :unit="unit"
                :selected="selected && !assigned"
                :dragging="dragging"
                :drag-offset="internalDragOffset"
                :editing="editing"
                :writable="writable"
                @resized="handleResizeBar">
            </gantt-unscheduled-flight-bar>
        </template>
        <template v-else>
            <gantt-flight-bar
                :flight="data"
                :start-date="startDate"
                :timezone="timezone"
                :selected="selected && !assigned"
                :assigned="assigned"
                :dragging="dragging"
                :drag-offset="internalDragOffset"
                :writable="writable">
            </gantt-flight-bar>
        </template>
    </div>
</template>

<script>
import GanttFlightBar from '@frontend_components/GanttFlightBar.vue';
import GanttMaintenanceBar from '@frontend_components/GanttMaintenanceBar.vue';
import GanttUnscheduledFlightBar from '@frontend_components/GanttUnscheduledFlightBar.vue';

export default {
    name: 'GanttBar',
    props: [
        'data', 'start-date', 'timezone', 'unit',
        'selected', 'assigned', 'dragging', 'drag-offset',
        'editing', 'writable',
    ],
    components: {
        'gantt-flight-bar': GanttFlightBar,
        'gantt-maintenance-bar': GanttMaintenanceBar,
        'gantt-unscheduled-flight-bar': GanttUnscheduledFlightBar,
    },
    data() {
        return {
            internalDragOffset: this.dragOffset,
        };
    },
    mounted() {
        this.initVueEventHandlers();
        this.initMouseEventHandlers();
    },
    beforeDestory() {
        this.unbindMouseEventHandlers();
    },
    methods: {
        initVueEventHandlers() {
            this.$on('drag-offset-update', (offset) => {
                this.internalDragOffset = offset;
            });
        },
        initMouseEventHandlers() {
            const barElement = this.$children[0].$el;
            $(this.$refs.ganttBar).on('mouseenter', this.handleMouseEnter.bind(this, barElement));
            $(this.$refs.ganttBar).on('mouseleave', this.handleMouseLeave.bind(this, barElement));
        },
        unbindMouseEventHandlers() {
            $(this.$refs.ganttBar).off('mouseenter');
            $(this.$refs.ganttBar).off('mouseleave');
        },
        handleMouseEnter(barElement) {
            if (!this.dragging) {
                this.$root.$emit('popover-show', barElement, this.data);
            }
        },
        handleMouseLeave() {
            if (!this.dragging) {
                this.$root.$emit('popover-hide');
            }
        },
        handleResizeBar(assignment_id, position, diff_seconds, vm) {
            this.$emit('resized', assignment_id, position, diff_seconds, vm);
        },
    },
}
</script>
