<template>
    <b-container>

        <b-row>
            <b-col>
                <p><i>imgs.ai</i> is a fast, dataset-agnostic, visual search engine for digital art history based on neural network embeddings. Its main feature is the concept of "re-search": results from a search can immediately form the basis of another search. This allows the intuitive exploration of an image corpus, while results are continuously refined.</p>
                <p><i>imgs.ai</i> utilizes modern approximate k-NN algorithms via <a href="https://github.com/spotify/annoy">Spotify's Annoy library</a> to deliver fast search results even for very large datasets in low-resource environments.</p>
            </b-col>
            
            <b-col>
                <b-img fluid src="static/img/met.gif"></b-img>
            </b-col>

        </b-row>

        <hr>

        <b-row>
            <b-col>
                <b-img fluid class="logo" src="static/img/fau.png"></b-img>
            </b-col>
            <b-col>
                <b-img fluid class="logo" src="static/img/ucsb.png"></b-img>
            </b-col>
        </b-row>
    </b-container>
</template>

<script>

export default {
    name: 'Index'

}
</script>

<style scoped>
.logo {
  max-height: 40px;
}
</style>