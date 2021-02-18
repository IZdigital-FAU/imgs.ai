<template>
    <b-card class="mt-3" header="Visual query">

        <b-row>
            <b-col>
                <b-img class="grid-item-img pos"
                    v-for="img in positiveImages" v-bind:key="img.id"
                    :src="img.url" :ref="img.id"></b-img>
            </b-col>
            <b-col>
                <b-img class="grid-item-img neg"
                    v-for="img in negativeImages" v-bind:key="img.id"
                    :src="img.url" :ref="img.id"></b-img>
            </b-col>
        </b-row>

        <b-button-group>
            <b-button variant="outline-danger">Remove</b-button>
            <b-button variant="outline-info">Clear</b-button>
        </b-button-group>

        <SearchPanel></SearchPanel>

        <b-button-group v-if="this.selected_imgs.length > 0">
            <b-button variant="success" @click="makePositive()">Positive</b-button>
            <b-button variant="danger" @click="makeNegative()">Negative</b-button>
        </b-button-group>

        <b-container fluid class="grid" ref="grid">
            <b-img class="grid-item-img"
                    v-for="img in imgs" v-bind:key="img.id"
                    :src="img.url" :ref="img.id"
                    @click="select(img)"></b-img>
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
        
        positiveImages: [
            {"id":"11108", "url":"https://www.moma.org/media/W1siZiIsIjc5NjEwIl0sWyJwIiwiY29udmVydCIsIi1xdWFsaXR5IDkwIC1yZXNpemUgMjAwMHgxNDQwXHUwMDNlIl1d.jpg?sha=0c2ae54e35d5b630"},
            {"id":"18151","url":"https://www.moma.org/media/W1siZiIsIjIwMDM5NCJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=691a73ad8e9ce228"},
            {"id":"51627","url":"https://www.moma.org/media/W1siZiIsIjIwMzM5OCJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=6cc2e602dd4458ab"}
        ],

        negativeImages: [
            {"id":"17032","url":"https://www.moma.org/media/W1siZiIsIjE4NjcxMyJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=24b8580d504a95dc"},
            {"id":"16851","url":"https://www.moma.org/media/W1siZiIsIjIxODQ4NSJdLFsicCIsImNvbnZlcnQiLCItcXVhbGl0eSA5MCAtcmVzaXplIDIwMDB4MTQ0MFx1MDAzZSJdXQ.jpg?sha=5e1791adb3f1e785"}
        ]
    }),

    // mounted(){
    //     this.$nextTick(() => {
            
    //     })
    // },

    created() {
        axios.get('api/images').then(response => {
            this.imgs = response.data.data
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

        makePositive(){
            this.selected_imgs.forEach(img => {
                this.positiveImages.push({id: img.id, url: img.url})
                
                this.update()
            })

            this.selected_imgs = []

        },

        update(){
            axios.get('api/images').then(response => {
                this.imgs = response.data.data
            })
        }
    }
}
</script>