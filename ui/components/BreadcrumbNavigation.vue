<script setup>
    import { computed } from 'vue'
    import { useRoute, useRouter } from 'vue-router'

    const route = useRoute()
    const router = useRouter()

    // Function to build breadcrumbs using route meta information
    const buildBreadcrumbs = () => {
        const path = route.path

        if (path === '/') {
            return [] // No breadcrumbs on home page
        }

        // Get all routes from the router to access meta information
        const routes = router.getRoutes()

        // Find route records that match the current path
        const currentRouteRecord = routes.find((r) => {
            if (r.path === path) return true

            // For routes with params like /characters/:id
            if (r.path.includes(':')) {
                const routePathParts = r.path.split('/')
                const currentPathParts = path.split('/')

                if (routePathParts.length === currentPathParts.length) {
                    return routePathParts.every(
                        (part, index) =>
                            part.startsWith(':') ||
                            part === currentPathParts[index],
                    )
                }
            }
            return false
        })

        if (!currentRouteRecord) {
            return [{ title: 'Home', to: '/' }]
        }

        const breadcrumbs = []

        // Add current route breadcrumb (without link since it's current page)
        if (currentRouteRecord.meta?.breadcrumb) {
            breadcrumbs.unshift({
                title: currentRouteRecord.meta.breadcrumb,
                to: undefined,
            })
        }

        // Handle parent relationship if defined in meta
        if (currentRouteRecord.meta?.parent) {
            const parentPath = currentRouteRecord.meta.parent
            const parentRoute = routes.find((r) => r.path === parentPath)

            if (parentRoute?.meta?.breadcrumb) {
                breadcrumbs.unshift({
                    title: parentRoute.meta.breadcrumb,
                    to: parentRoute.path,
                })
            }
        }

        // Always add Home as the first breadcrumb (unless we're already at home)
        if (breadcrumbs.length > 0 && breadcrumbs[0].to !== '/') {
            breadcrumbs.unshift({ title: 'Home', to: '/' })
        }

        return breadcrumbs
    }

    const breadcrumbs = computed(() => buildBreadcrumbs())

    // Computed property that converts to Vuetify format
    const vuetifyBreadcrumbs = computed(() =>
        breadcrumbs.value.map((item) => ({
            title: item.title,
            to: item.to ? String(item.to) : undefined,
            disabled: item.disabled || !item.to,
        })),
    )
</script>

<template>
  <v-toolbar
    density="compact"
    class="mb-4"
  >
    <v-breadcrumbs :items="vuetifyBreadcrumbs">
      <template #item="{ item }">
        <v-breadcrumbs-item
          :title="item.title"
          :to="item.to || undefined"
          :disabled="item.disabled"
        />
      </template>
    </v-breadcrumbs>
  </v-toolbar>
</template>
