import ImageGrid from "./components/interface/ImageGrid.vue";
import Embedder from "./components/embedder/Embedder.vue";
import Index from './components/Index.vue';
import Help from './components/Help.vue';

export const routes = [
    {path: '/', component: Index},
    {path: '/interface', component: ImageGrid},
    {path: '/embedder', component: Embedder},
    {path: '/help', component: Help}
  ]