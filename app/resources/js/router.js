import ImageGrid from "./components/interface/ImageGrid.vue";
import Embedder from "./components/embedder/Embedder.vue";
import ProjectIndex from './components/projects/ProjectIndex.vue'
import ProjectShow from './components/projects/ProjectShow.vue'

import Index from './components/Index.vue';
import Help from './components/Help.vue';

export const routes = [
    {path: '/', name: 'home', component: Index},
    {path: '/interface', name: 'interface', component: ImageGrid},
    {path: '/embedder', name: 'embedder', component: Embedder},
    {path: '/projects', name: 'projects.index', component: ProjectIndex},
    {path: '/projects/:id', name: 'project.show', component: ProjectShow},
    {path: '/help', name: 'help', component: Help}
  ]