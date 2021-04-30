<template>
    <div>
        <b-table        
            hover
            :busy="loading"
            :items="items"
            :fields="fields"
            :selectable="selectable"
            select-mode="multi"
            @row-selected="onRowSelected"
            @row-dblclicked="onRowDblClicked">

            <template #cell(name)="{ item, rowSelected }">
                <template v-if="rowSelected">
                    <span aria-hidden="true">✅</span> {{item.name}}
                    <span class="sr-only">Selected</span>
                </template>
                <template v-else>
                    <span aria-hidden="true">&nbsp;</span> {{item.name}}
                    <span class="sr-only">Not selected</span>
                </template>
            </template>

            <template #table-busy>
                <div class="text-center text-danger my-2">
                    <b-spinner class="align-middle"></b-spinner>
                    <strong>Loading...</strong>
                </div>
            </template>

            <template v-for="(_, slot) of $scopedSlots" v-slot:[slot]="scope">
                <slot :name="slot" v-bind="scope"/>
            </template>
        </b-table>

        <b-pagination v-if="Object.keys(pagination).length > 0" @page-click="getPage" v-model="pagination.currentPage"
                        :per-page="pagination.per_page" :total-rows="pagination.total"
                        first-text="⏮" last-text="⏭"
                        pills align="center">

            <template #prev-text>
                <b-icon icon="chevron-left"></b-icon>
            </template>

            <template #next-text>
                <b-icon icon="chevron-right"></b-icon>
            </template>

        </b-pagination>
    </div>
</template>


<script>
export default {
    name: 'Pagination',

    props: {
        items: Array,
        fields: Array,
        loading: Boolean,
        selectable: Boolean,
        pagination: Object
    },

    methods: {
        onRowSelected() {
            this.$emit('onRowSelected')
        },

        onRowDblClicked(item, index) {
            this.$emit('onRowDblClicked', item, index)
        },

        getPage(event, page) {
            this.$emit('getPage', event, page)
        }
    }

}
</script>