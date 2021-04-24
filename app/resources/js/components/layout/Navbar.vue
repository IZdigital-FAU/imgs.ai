<template>
    <b-navbar toggleable="lg" type="dark" variant="info">
        
        <b-avatar v-b-toggle.sidebar-1 variant="light" icon="list" class="mr-5"></b-avatar>
        
        <b-navbar-brand :to="{name: 'home'}">imgs.ai</b-navbar-brand>

        <b-collapse id="nav-collapse" is-nav>
        <b-navbar-nav>
            <b-nav-item :to="{name: 'interface'}">Interface</b-nav-item>
            <b-nav-item :to="{name: 'projects.index'}">Projects</b-nav-item>
        </b-navbar-nav>

        <!-- Right aligned nav items -->
        <b-navbar-nav class="ml-auto">

            <b-nav-item-dropdown right>
                <!-- Using 'button-content' slot -->
                <template #button-content>
                    <em>User</em>
                </template>

                <b-dropdown-item href="#">Profile</b-dropdown-item>
                <b-dropdown-item href="/auth/logout">Sign Out</b-dropdown-item>

            </b-nav-item-dropdown>

            <b-nav-item :to="{name: 'help'}">Help <b-icon icon="question-circle"></b-icon></b-nav-item>

        </b-navbar-nav>
        </b-collapse>
    </b-navbar>
</template>

<script>

export default {
    name: 'Navbar',

}
</script>