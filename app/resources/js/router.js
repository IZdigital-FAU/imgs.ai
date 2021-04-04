import ImageGrid from "./components/interface/ImageGrid.vue";
import Embedder from "./components/embedder/Embedder.vue";

export const routes = [
    {path: '/interface', component: ImageGrid},
    {path: '/embedder', component: Embedder}
  ]