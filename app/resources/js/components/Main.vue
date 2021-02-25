<template>
    <div>
        {{$route}}
        <ImageGrid v-if="$route.path === '/interface'"></ImageGrid>
        <Embedder v-else-if="$route.path === '/embedder'"></Embedder>
    </div>
</template>

<script>
import ImageGrid from './interface/ImageGrid.vue'
import Embedder from './embedder/Embedder.vue'

export default {
    name: 'Main',
    components: {ImageGrid, Embedder},
}
</script>