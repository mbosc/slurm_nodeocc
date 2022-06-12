package main

import (
	"fmt"
	"os"

	// "github.com/brianvoe/gofakeit"

	// table "github.com/calyptia/go-bubble-table"

	tea "github.com/charmbracelet/bubbletea"
	"github.com/charmbracelet/lipgloss"

	"github.com/mbosc/stickers"
	"golang.org/x/term"
)

func main() {
	os.Setenv("TERM", "xterm-256color")
	err := tea.NewProgram(initialModel(), tea.WithAltScreen()).Start()
	if err != nil {
		fmt.Fprintln(os.Stderr, err)
		os.Exit(1)
	}
}

var (
	styleDoc = lipgloss.NewStyle().Padding(1)
)

// TODO
// - replace stopwatch with pipe reader

type newDataMsg struct {
	Joblets []Joblet
	Jobs    []Job
}

func runPipeReader() tea.Msg {
	// fmt.Println("runPipeReader on file " + "/tmp/noccfifo_" + os.Getenv("USER"))
	// Joblets, Jobs := GetDump("../nocc.txt").GetJoblets()
	Joblets, Jobs := GetDump("/tmp/noccfifo_" + os.Getenv("USER")).GetJoblets()
	return newDataMsg{Joblets, Jobs}
}

func fillTable(tbl *stickers.Table, joblets []Joblet, jobs []Job) {
	rows := make([][]any, len(joblets))
	for i := 0; i < len(joblets); i++ {
		rows[i] = make([]any, len(tbl.ColumnHeaders))
		rows[i][0] = joblets[i].JobId
		rows[i][1] = jobs[i].Name
		rows[i][2] = jobs[i].User
		rows[i][3] = jobs[i].State
		rows[i][4] = jobs[i].Runtime
		rows[i][5] = fmt.Sprintf("%d", joblets[i].Mem)
		rows[i][6] = fmt.Sprintf("%d gpu", joblets[i].NGpus)
		rows[i][7] = jobs[i].Reason
	}
	tbl.AddRows(rows)
}

func initialModel() model {
	w, h, err := term.GetSize(int(os.Stdout.Fd()))
	if err != nil {
		w = 80
		h = 24
	}
	w = 20
	top, right, bottom, left := styleDoc.GetPadding()
	w = w - left - right
	h = h - top - bottom
	// tbl := table.New([]string{"ID", "NAME", "USER", "ST", "TIME", "MEM", "GP", "REASON"}, w, h)
	headers := []string{"ID", "NAME", "USER", "ST", "TIME", "MEM", "GP", "REASON"}
	tbl := stickers.NewTable(0, 0, headers)
	return model{table: *tbl}
}

type model struct {
	table stickers.Table
}

func (m model) Init() tea.Cmd {
	return runPipeReader
}

func (m model) Update(msg tea.Msg) (tea.Model, tea.Cmd) {
	switch msg := msg.(type) {
	case newDataMsg:
		// empty table
		m.table.Rows = make([][]any, 0)

		// fill table
		fillTable(&m.table, msg.Joblets, msg.Jobs)

		return m, runPipeReader
	case tea.WindowSizeMsg:
		top, right, bottom, left := styleDoc.GetPadding()
		m.table.SetWidth(msg.Width - left - right)
		m.table.SetHeight(msg.Height - top - bottom)
	case tea.KeyMsg:
		switch msg.String() {
		case "ctrl+c":
			return m, tea.Quit
		case "down":
			m.table.CursorDown()
		case "up":
			m.table.CursorUp()
		case "left":
			m.table.CursorLeft()
		case "right":
			m.table.CursorRight()
		case "ctrl+s":
			x, _ := m.table.GetCursorLocation()
			m.table.OrderByColumn(x)
		}
	}

	// var cmd tea.Cmd
	// m.table, cmd = m.table.Update(msg)
	// return m, cmd
	return m, nil
}

func (m model) View() string {
	return styleDoc.Render(
		m.table.Render(),
	)
}
