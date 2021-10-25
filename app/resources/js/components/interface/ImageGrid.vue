<template>
    <div>
        <b-card class="mt-3 ml-3 mr-3">
            <b-row>
                <b-col>
                    <b-img class="query-img"
                        v-for="img in positiveImages" :key="img.id"
                        :src="img.url" :ref="img.id"
                        @click="selectQuery(img)">

                        <b-btn-group><b-btn class="imgSettings">Button 1</b-btn></b-btn-group>

                    </b-img>
                </b-col>
                <b-col>
                    <b-img class="query-img"
                        v-for="img in negativeImages" :key="img.id"
                        :src="img.url" :ref="img.id"
                        @click="selectQuery(img)"></b-img>
                </b-col>
            </b-row>
            
            <CarouselModal :slide="slide"></CarouselModal>

        </b-card>

        <b-overlay :show="loading" spinner-type="grow">
            <b-container fluid class="mt-2">
                <stack
                    :column-min-width="200"
                    :gutter-width="15"
                    :gutter-height="15"
                    monitor-images-loaded>
                    <stack-item
                            v-for="img in imgs" :key="img.id"
                            style="transition: transform 300ms">
                        
                        <b-img :src="img.url" fluid :ref="img.id"
                            @dblclick="openModal(img)"
                            @click="select(img)"
                        ></b-img>

                    </stack-item>
                </stack>
            </b-container>

            <Toolbar 
                     :positiveImages="positiveImages"
                     :negativeImages="negativeImages"
                     :embedders="embedders"
                     :selected_imgs="selected_imgs"
                     :selected_query_imgs="selected_query_imgs"
                     :query="querySelection"
                     @makePositive="makePositive"
                     @makeNegative="makeNegative"
                     @clear="clear"
                     @remove="remove"
                     @update="update">
            </Toolbar>

        </b-overlay>
    </div>
</template>

<script>
import axios from 'axios'

import SearchPanel from './SearchPanel.vue'
import CarouselModal from './CarouselModal.vue'
import Toolbar from './Toolbar.vue'

import { Stack, StackItem } from 'vue-stack-grid';

export default {
    name: 'ImageGrid',
    components: {SearchPanel, CarouselModal, Toolbar, Stack, StackItem},

    data : () => ({
        imgs: [],
        selected_imgs: [],
        selected_query_imgs: [],
        
        positiveImages: [],
        negativeImages: [],

        querySelection: {},
        embedders: [],
        
        slide: 0,

        loading: true,

        csrf: document.querySelector('#csrf').value
    }),

    async created() {
        await axios.get('api/images').then(response => {
            this.imgs = response.data.data
            this.querySelection = response.data.querySelection
            this.embedders = response.data.embedders
        })

        this.loading = false;

        // this.$nextTick(function () {
        //     window.dispatchEvent(new Event('resize'));
        // })
    },

    activated() {
        window.dispatchEvent(new Event('resize'));
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
            this.querySelection.pos = this.positiveImages.map(img => img.id)
            this.querySelection.neg = this.negativeImages.map(img => img.id)

            axios.post('api/images', this.querySelection, {headers: {"X-CSRFToken": this.csrf}})
                .then(response => {
                    this.imgs = response.data.data.filter(item => !this.positiveImages.map(o => o.id).includes(item.id) && !this.negativeImages.map(o => o.id).includes(item.id))
                    this.querySelection = response.data.querySelection
                })

            var evt = window.document.createEvent('UIEvents'); 
            evt.initUIEvent('resize', true, false, window, 0); 
            window.dispatchEvent(evt);
        },

        remove() {
            this.selected_query_imgs.forEach(img => {
                let posIdx = this.positiveImages.map(pos => pos.id)
                let negIdx = this.negativeImages.map(neg => neg.id)

                if (posIdx.includes(img.id)) this.positiveImages.splice(posIdx.indexOf(img.id), 1)
                else if (negIdx.includes(img.id)) this.negativeImages.splice(negIdx.indexOf(img.id), 1)
            })
            this.selected_imgs = [];
            this.selected_query_imgs = [];
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
        },

        selectQuery(img) {
            if (!this.selected_query_imgs.includes(img)) {
                this.selected_query_imgs.push(img)
                var imgElem = this.$refs[img.id][0]
                imgElem.classList.add('active')
            } else {
                this.selected_query_imgs.splice(this.selected_query_imgs.indexOf(img))
                var imgElem = this.$refs[img.id][0]
                imgElem.classList.remove('active')
            }
        }
    }
}
</script>

<style scoped>
.query-img {
    width: 15vw;
}

.active {
    border-style: solid;
    border-color: #007bff;
}


.imgSettings {
    position: absolute;
}
</style>