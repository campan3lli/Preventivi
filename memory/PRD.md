# PRD - Limone Blu Studio Quote Generator

## Original Problem Statement
Webapp interna per agenzia di comunicazione Limone Blu Studio per creare preventivi velocemente nel template aziendale. Interfaccia semplice con checkbox per selezionare servizi, anagrafica clienti e fornitori, generazione PDF e invio email.

## User Personas
- **Operatori agenzia**: Utenti interni che creano preventivi per clienti
- **Amministratori**: Gestiscono listino prezzi e fornitori

## Core Requirements (Static)
- 4 tipologie preventivo: Standard, A Step, Moduli, Ibrido
- Anagrafica clienti: Nome azienda, P.IVA, Indirizzo, Email, Telefono
- Listino servizi modificabile con prezzi
- Generazione PDF nel template Limone Blu Studio
- Invio email con PDF allegato
- Storico preventivi salvato
- Branding: #002fa7, #dbf637, #ffffff, #1a281f - Font Raleway

## What's Been Implemented (Jan 2026)
- ✅ Dashboard con statistiche (preventivi, clienti, servizi, totale)
- ✅ CRUD completo Clienti (crea, modifica, elimina, cerca)
- ✅ CRUD completo Servizi (36 servizi precaricati con prezzi)
- ✅ CRUD completo Fornitori (5 fornitori precaricati)
- ✅ Creazione preventivo in 3 step wizard
- ✅ 4 tipologie preventivo (Standard, A Step, Moduli, Ibrido)
- ✅ Selezione servizi con checkbox e riepilogo totale
- ✅ Generazione PDF con template blu copertina
- ✅ Download PDF funzionante
- ✅ Modal invio email con allegato PDF (richiede Resend API key)
- ✅ Storico preventivi con filtri
- ✅ Aggiornamento stato preventivo (Bozza, Inviato, Accettato, Rifiutato)
- ✅ Sidebar navigazione con logo Limone Blu
- ✅ Design responsive con palette aziendale

## Prioritized Backlog
### P0 (Critical)
- Nessuno

### P1 (High)
- Configurare Resend API key per invio email reale
- Implementare gestione Step per preventivi "A Step" e "Ibrido"

### P2 (Medium)
- Export preventivi in Excel
- Duplicazione preventivo esistente
- Template email personalizzabili
- Report statistiche avanzate

## Next Tasks
1. Configurare RESEND_API_KEY nel backend/.env per attivare invio email
2. Aggiungere gestione Step/Fasi per preventivi complessi
3. Migliorare template PDF con più dettagli (logo vettoriale, footer)
