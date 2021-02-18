<template>
    <b-card class="mt-3" header="Visual query">
        <SearchPanel @update="update"></SearchPanel>
        <CarouselModal></CarouselModal>

        <b-button-group v-if="this.selected_imgs.length > 0">
            <b-button variant="success" @click="makePositive()">Positive</b-button>
            <b-button variant="danger" @click="makeNegative()">Negative</b-button>
        </b-button-group>

        <b-container fluid ref="grid">
            <b-img class="grid-item-img"
                    v-for="img in imgs" v-bind:key="img.id"
                    :src="img.url" :ref="img.id"
                    @click="select(img)"
                    @dblclick="$bvModal.show('carouselmodal')"></b-img>
        </b-container>
    </b-card>
</template>

<script>
import axios from 'axios'
var Packery = require('packery')

import SearchPanel from './SearchPanel.vue'
import CarouselModal from './CarouselModal.vue'

export default {
    name: 'Interface',
    components: {SearchPanel, CarouselModal},

    data : () => ({
        imgs: [],
        selected_imgs: [],
        
        positiveImages: [],
        negativeImages: [],

        querySelection: {
            data: 'moma',
            embedder: 'vgg19',
            order: 'rank',
            distance: 'manhattan',
            n: 30
        }
    }),

    // mounted(){
    //     this.$nextTick(() => {
            
    //     })
    // },

    async created() {
        await axios.get('api/images').then(response => {
            this.imgs = response.data.data
        })
        var elem = this.$refs.grid

        var pckry = new Packery( elem, {
            itemSelector: '.grid-item-img',
            gutter: 3,
            percentPosition: true,
            columnWidth: 10,
        });
    },

    methods: {
        select(img) {
            if (!this.selected_imgs.includes(img)) {
                this.selected_imgs.push(img)
                var imgElem = this.$refs[img.id][0]
                imgElem.classList.add('active')

            } else {
                this.selected_imgs.splice(this.selected_imgs.indexOf(img))
                var imgElem = this.$refs[img.id][0]
                imgElem.classList.remove('active')
            }
        },

        async makePositive(){
            this.selected_imgs.forEach(img => {
                this.positiveImages.push({id: img.id, url: img.url})
            })

            await this.update()
            this.selected_imgs = []
        },

        async makeNegative(){
            this.selected_imgs.forEach(img => {
                this.negativeImages.push({id: img.id, url: img.url})
            })

            await this.update()
            this.selected_imgs = []
        },

        update(){
            axios.post('api/images', {
                posIdxs: this.positiveImages.map(img => img.id),
                negIdxs: this.negativeImages.map(img => img.id),
                data: this.querySelection.data,
                embedder: this.querySelection.embedder,
                order: this.querySelection.order,
                distance: this.querySelection.distance,
                n: this.querySelection.n
            }).then(response => {
                this.imgs = response.data.data.filter(item => !this.positiveImages.map(o => o.id).includes(item.id) && !this.negativeImages.map(o => o.id).includes(item.id))
            }).finally(() => {
                var elem = this.$refs.grid

                var pckry = new Packery( elem, {
                    itemSelector: '.grid-item-img',
                    gutter: 3,
                    percentPosition: true,
                    columnWidth: 10,
                });
            })
        },

        remove() {
            this.selected_imgs = [];
        },

        clear() {
            this.positiveImages = [];
            this.negativeImages = [];
            this.update()
        }
    }
}
</script>