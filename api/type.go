package api

type Git struct {
	URL         string
	AccessToken string
	Username    string
	Password    string
}

type Repo struct {
	Name        string
	Private     bool
	Description string
}

func (g *Git) Auth() error {
	return nil
}

func (g *Git) AddSSHKey(key string) error {
	return nil
}

func (g *Git) CreateRepo(repo *Repo) error {
	return nil
}

func (g *Git) ListRepos() (repos []*Repo, err error) {

	return nil, nil
}

func (g *Git) DeleteRepo() error {
	return nil
}
