<template>
    <b-card class="mt-3" header="Visual query">

        <b-row>
            <b-col>
                <b-img class="grid-item-img pos"
                    v-for="(url, id) in posImgs" v-bind:key="id"
                    :src="url" :value="id"></b-img>
            </b-col>
            <b-col>
                <b-img class="grid-item-img neg"
                    v-for="(url, id) in negImgs" v-bind:key="id"
                    :src="url" :value="id"></b-img>
            </b-col>
        </b-row>

        <b-button-group>
            <b-button variant="outline-danger">Remove</b-button>
            <b-button variant="outline-info">Clear</b-button>
        </b-button-group>

        <SearchPanel></SearchPanel>

        <b-container fluid class="grid" ref="grid">
            <b-img class="grid-item-img"
                    v-for="(url, id) in imgs" v-bind:key="id"
                    :src="url" :value="id"></b-img>
        </b-container>
    </b-card>
</template>

<script>
import axios from 'axios'
var Packery = require('packery')

import SearchPanel from './SearchPanel.vue'

export default {
    name: 'Interface',
    components: {SearchPanel},

    data : () => ({
        imgs: {},
        selected_imgs: [],
        posImgs: {"538": "https://www.moma.org/media/W1siZiIsIjY1NjgiXSxbInAiLCJjb252ZXJ0IiwiLXF1YWxpdHkgOTAgLXJlc2l6ZSAyMDAweDE0NDBcdTAwM2UiXV0.jpg?sha=0c7fa826b79591a1",
  "3268": "https://www.moma.org/media/W1siZiIsIjEzOTkiXSxbInAiLCJjb252ZXJ0IiwiLXF1YWxpdHkgOTAgLXJlc2l6ZSAyMDAweDE0NDBcdTAwM2UiXV0.jpg?sha=5a54380db90100a5",
  "4225": "https://www.moma.org/media/W1siZiIsIjIxMTQ3OSJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=64f1ca5b051f29b5",},
        negImgs: {  "43022": "https://www.moma.org/media/W1siZiIsIjIyMzU0MCJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=1bdd50830d35f3f8",
  "46871": "https://www.moma.org/media/W1siZiIsIjI1MDczOSJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=b0179f39b454011e",
  "48974": "https://www.moma.org/media/W1siZiIsIjE2OTI4NyJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=f4c1e13e4462ac1b",}
    }),

    // mounted(){
    //     this.$nextTick(() => {
            
    //     })
    // },

    created() {
        axios.get('api/images').then(response => {
            this.imgs = response.data
        }).finally(() => {
            var elem = this.$refs.grid

            var pckry = new Packery( elem, {
                itemSelector: '.grid-item-img',
                gutter: 3,
                percentPosition: true,
                columnWidth: 10,
            });
        })
    }
}
</script>