<template>
    <b-modal id="carouselmodal" title="imgs.ai" hide-footer>
         <b-carousel
            id="imgs"
            v-model="slide"
            :interval="4000"
            controls
            indicators
            background="#ababab"
            img-width="1024"
            img-height="480"
            style="text-shadow: 1px 1px 2px #333;"
            @sliding-start="onSlideStart"
            @sliding-end="onSlideEnd"
            >
            <b-carousel-slide
                v-for="img in imgs"
                text="Nulla vitae elit libero, a pharetra augue mollis interdum."
                :img-src="img.url"
            ></b-carousel-slide>
        </b-carousel>
    </b-modal>
</template>

<script>
export default {
    name: 'SearchPanel',
    props: {
        slide: Number
    },

    data : () => ({
        sliding: null
    }),

    computed: {
        imgs() {
            return this.$parent.imgs
        }
    },

    methods: {
      onSlideStart(slide) {
        this.sliding = true
      },
      onSlideEnd(slide) {
        this.sliding = false
      }
    }
}
</script>