document.querySelectorAll('.delete-btn').forEach(button => {
    button.addEventListener('click', function() {
        const medicamentId = this.getAttribute('data-id');
        Swal.fire({
            title: 'Êtes-vous sûr de vouloir supprimer ce médicament?',
            text: "Vous ne pourrez pas revenir en arrière !",
            icon: 'warning',
            showCancelButton: true,
            confirmButtonColor: '#3085d6',
            cancelButtonColor: '#d33',
            confirmButtonText: 'Oui, supprimez-le !'
        }).then((result) => {
            if (result.isConfirmed) {
                fetch(`{% url 'supprimer_medicament' 0 %}`.replace('/0/', `/${medicamentId}/`), {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json',
                        'X-CSRFToken': '{{ csrf_token }}'
                    },
                    body: JSON.stringify({ id: medicamentId })
                }).then(response => {
                    if (response.ok) {
                        Swal.fire(
                            'Supprimé !',
                            'Le médicament a été supprimé.',
                            'success'
                        ).then(() => {
                            location.reload();
                        });
                    } else {
                        Swal.fire(
                            'Erreur !',
                            'Il y a eu un problème lors de la suppression.',
                            'error'
                        );
                    }
                });
            }
        });
    });
});