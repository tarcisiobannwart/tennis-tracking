import SwiftUI

struct ContentView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        Group {
            if appState.isLoggedIn {
                MainTabView()
                    .transition(.opacity)
            } else {
                LoginView()
                    .transition(.opacity)
            }
        }
        .animation(.easeInOut(duration: 0.3), value: appState.isLoggedIn)
    }
}

struct MainTabView: View {
    @EnvironmentObject var appState: AppState

    var body: some View {
        TabView {
            NavigationStack {
                MatchListView()
            }
            .tabItem {
                Label("Partidas", systemImage: "sportscourt")
            }

            NavigationStack {
                SettingsView()
            }
            .tabItem {
                Label("Ajustes", systemImage: "gearshape")
            }
        }
        .tint(Color.courtGreen)
    }
}

#Preview {
    ContentView()
        .environmentObject(AppState())
}
