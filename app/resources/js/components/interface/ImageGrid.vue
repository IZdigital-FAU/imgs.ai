<template>
    <b-card class="mt-3" header="Visual query">
        <b-row>
            <b-col>
                <b-row>
                    <b-col>
                        <b-img class="grid-item-img pos"
                            v-for="img in positiveImages" v-bind:key="img.id"
                            :src="img.url" :ref="img.id"
                            @click="select(img)"></b-img>
                    </b-col>
                    <b-col>
                        <b-img class="grid-item-img neg"
                            v-for="img in negativeImages" v-bind:key="img.id"
                            :src="img.url" :ref="img.id"
                            @click="select(img)"></b-img>
                    </b-col>
                </b-row>

                <b-button-group>
                    <b-button variant="outline-danger" @click="remove()">Remove</b-button>
                    <b-button variant="outline-info" @click="clear()">Clear</b-button>
                </b-button-group>
            </b-col>
            <b-col>
                <SearchPanel @update="update"></SearchPanel>
            </b-col>
        </b-row>
        
        <CarouselModal :slide="slide"></CarouselModal>

        <b-button-group v-if="this.selected_imgs.length > 0">
            <b-button variant="success" @click="makePositive()">Positive</b-button>
            <b-button variant="danger" @click="makeNegative()">Negative</b-button>
        </b-button-group>

        <b-container fluid ref="grid">
            <b-img class="grid-item-img"
                    v-for="img in imgs" v-bind:key="img.id"
                    :src="img.url" :ref="img.id"
                    @click="select(img)"
                    @dblclick="openModal(img)"></b-img>
        </b-container>
    </b-card>
</template>

<script>
import axios from 'axios'

var Masonry = require('masonry-layout');

import SearchPanel from './SearchPanel.vue'
import CarouselModal from './CarouselModal.vue'

export default {
    name: 'ImageGrid',
    components: {SearchPanel, CarouselModal},

    data : () => ({
        imgs: [],
        selected_imgs: [],
        
        positiveImages: [],
        negativeImages: [],

        querySelection: {},

        msnry: {},
        
        slide: 0
    }),

    async created() {
        await axios.get('api/images').then(response => {
            this.imgs = response.data.data
            this.querySelection = response.data.querySelection
        })

        this.msnry = new Masonry(this.$refs.grid, {
            itemSelector: '.grid-item-item',
            columnWidth: 10
        });

        console.log('my masonry:', this.msnry.items.map(i => i.element))

        this.msnry.on( 'layoutComplete', function( items ) {
            console.log('layoutComplete', items.length );
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
            this.querySelection.pos_idxs = this.positiveImages.map(img => img.id)
            this.querySelection.neg_idxs = this.negativeImages.map(img => img.id)

            axios.post('api/images', this.querySelection)
                .then(response => {
                    this.imgs = response.data.data.filter(item => !this.positiveImages.map(o => o.id).includes(item.id) && !this.negativeImages.map(o => o.id).includes(item.id))
                    this.querySelection = response.data.querySelection
                })
        },

        remove() {
            this.selected_imgs.forEach(img => {
                let posIdx = this.positiveImages.map(pos => pos.id)
                let negIdx = this.negativeImages.map(neg => neg.id)

                console.log('posIdx', posIdx)
                console.log('imgID', img.id)

                if (posIdx.includes(img.id)) this.positiveImages.splice(posIdx.indexOf(img.id), 1)
                else if (negIdx.includes(img.id)) this.negativeImages.splice(negIdx.indexOf(img.id), 1)
            })
            this.selected_imgs = [];
            this.update()
        },

        clear() {
            this.positiveImages = [];
            this.negativeImages = [];
            this.update()
        },

        openModal(img) {
            this.slide = this.imgs.map(item => item.id).indexOf(img.id)
            this.$bvModal.show('carouselmodal')
        }
    }
}
</script>

<style scoped>
.grid-item-img.pos {
  width: 30%;
}

.grid-item-img.neg {
  width: 30%;
}

.grid-item-img {
    width: 200px;
}

.grid-item-img.active {box-shadow: 0px 0px 10px 0px red;}
</style>