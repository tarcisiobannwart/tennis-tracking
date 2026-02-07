package com.tennistrack.app.ui.screens;

import androidx.compose.foundation.layout.Arrangement;
import androidx.compose.material.icons.Icons;
import androidx.compose.material3.CardDefaults;
import androidx.compose.material3.ExperimentalMaterial3Api;
import androidx.compose.material3.TopAppBarDefaults;
import androidx.compose.runtime.Composable;
import androidx.compose.ui.Alignment;
import androidx.compose.ui.Modifier;
import androidx.compose.ui.text.font.FontWeight;
import androidx.compose.ui.text.style.TextOverflow;
import com.tennistrack.app.data.model.MatchResponse;
import com.tennistrack.app.ui.viewmodels.MatchListViewModel;

@kotlin.Metadata(mv = {1, 9, 0}, k = 2, xi = 48, d1 = {"\u0000.\n\u0000\n\u0002\u0010\u0002\n\u0000\n\u0002\u0010\u000e\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0000\n\u0002\u0018\u0002\n\u0002\b\u0002\n\u0002\u0018\u0002\n\u0002\b\u0003\n\u0002\u0018\u0002\n\u0002\b\u0003\u001a\u0010\u0010\u0000\u001a\u00020\u00012\u0006\u0010\u0002\u001a\u00020\u0003H\u0003\u001a\u001e\u0010\u0004\u001a\u00020\u00012\u0006\u0010\u0005\u001a\u00020\u00062\f\u0010\u0007\u001a\b\u0012\u0004\u0012\u00020\u00010\bH\u0003\u001aB\u0010\t\u001a\u00020\u00012\u0012\u0010\n\u001a\u000e\u0012\u0004\u0012\u00020\u0003\u0012\u0004\u0012\u00020\u00010\u000b2\f\u0010\f\u001a\b\u0012\u0004\u0012\u00020\u00010\b2\f\u0010\r\u001a\b\u0012\u0004\u0012\u00020\u00010\b2\b\b\u0002\u0010\u000e\u001a\u00020\u000fH\u0007\u001a\u0010\u0010\u0010\u001a\u00020\u00012\u0006\u0010\u0011\u001a\u00020\u0003H\u0003\u00a8\u0006\u0012"}, d2 = {"InfoChip", "", "text", "", "MatchCard", "match", "Lcom/tennistrack/app/data/model/MatchResponse;", "onClick", "Lkotlin/Function0;", "MatchListScreen", "onMatchSelected", "Lkotlin/Function1;", "onNewStream", "onSettingsClick", "viewModel", "Lcom/tennistrack/app/ui/viewmodels/MatchListViewModel;", "StatusBadge", "status", "app_debug"})
public final class MatchListScreenKt {
    
    @kotlin.OptIn(markerClass = {androidx.compose.material3.ExperimentalMaterial3Api.class})
    @androidx.compose.runtime.Composable()
    public static final void MatchListScreen(@org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function1<? super java.lang.String, kotlin.Unit> onMatchSelected, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onNewStream, @org.jetbrains.annotations.NotNull()
    kotlin.jvm.functions.Function0<kotlin.Unit> onSettingsClick, @org.jetbrains.annotations.NotNull()
    com.tennistrack.app.ui.viewmodels.MatchListViewModel viewModel) {
    }
    
    @androidx.compose.runtime.Composable()
    private static final void MatchCard(com.tennistrack.app.data.model.MatchResponse match, kotlin.jvm.functions.Function0<kotlin.Unit> onClick) {
    }
    
    @androidx.compose.runtime.Composable()
    private static final void StatusBadge(java.lang.String status) {
    }
    
    @androidx.compose.runtime.Composable()
    private static final void InfoChip(java.lang.String text) {
    }
}