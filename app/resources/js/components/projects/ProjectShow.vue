<template>
        <b-jumbotron>
        <b-form @submit="post">
            <b-row>
                <b-col>
                    <b-form-group
                        id="name"
                        label="Project name:"
                        label-for="name"
                        description="Give your image collection a suggestive name"
                    >
                        <b-form-input v-model="model.name" :placeholder="model.name" required id="name"></b-form-input>
                    </b-form-group>
                </b-col>
                <b-col>
                    
                </b-col>
            </b-row>

            <b-list-group>
                
                <b-list-group-item v-for="img in imgs" v-bind:key="img.url">
                    {{img}}
                </b-list-group-item>

            </b-list-group>

            <b-button type="submit" variant="outline-primary">Embed</b-button>
        </b-form>
    </b-jumbotron>
</template>

<script>
import axios from 'axios'

export default {
    name: 'ProjectShow',

    data() {
        return {
            model: {},
            imgs: [],

            csrf: document.querySelector('#csrf').value
        }
    },

    created() {
        this.model = this.$route.params

        axios.get(`/api/project/${this.model.id}`).then(resp => {
            this.imgs = resp.data
        })
    },

    methods: {
        post() {
            console.log('hi')
        }
    }
}
</script>