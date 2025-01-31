from typing import ValuesView
from django.db.models import fields
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.views.generic.edit import FormView, CreateView, UpdateView, DeleteView
from django.views import View
from django.urls import reverse_lazy
from datetime import date, timedelta

from .forms import ClientForm, LoginForm, EmployeeAddForm, EmployeeEditForm, VariantForm, CartForm
from .models import ORDER_STATUS, Batch, CalendarSupervisor, Client, Employee, Branch, Product, Variant, Order, Cart, CLIENT_TYPE
from django.contrib.auth.models import User

class LoginView(View):
    """View created for login page

    Args:
        LoginForm (class): Form with login and password
    """
    def get(self, request):
        form = LoginForm()
        return render(request, 'manager_app/login.html', {'form': form})

    def post(self, request):
        form = LoginForm(request.POST)
        if form.is_valid():
            user = authenticate(
                username=form.cleaned_data['login'], 
                password=form.cleaned_data['password']
            )
            if user:
                login(request, user)
                return redirect('/')
            else:
                return render(request, 'manager_app/login.html', {'form': form, 'answer': 'Błędny login lub hasło'})
        else: 
            return render(request, 'manager_app/login.html', {'form': form})


class LogoutView(View):
    """
    View created fo logout
    """
    def get(self, request):
        logout(request)
        return redirect("/login/")


class DashbaordView(LoginRequiredMixin, View):
    """
    Dashbord View - calendar of supervisor, monthly statistics of team.
    Login required.
    """
    def get(self, request):
        today = date.today()
        days_in_calendar = 5
        
        year, month, day = (int(x) for x in str(today).split('-'))
        weekday = today.weekday()
        
        last_monday = today - timedelta(days = weekday )
        this_week = {}
        for i in range(days_in_calendar):
            final_date = last_monday + timedelta(days = i - 1)
            meeting = CalendarSupervisor.objects.filter(date = final_date, owner = request.user.employee)
            this_week[final_date] = meeting
        
        last_week_monday = last_monday - timedelta(days = 7)
        last_week = {}
        for i in range(days_in_calendar):
            final_date = last_week_monday + timedelta(days = i - 1)
            meeting = CalendarSupervisor.objects.filter(date = final_date, owner = request.user.employee)
            last_week[final_date] = meeting
        
        next_monday = last_monday + timedelta( days=7)
        next_week = {}
        for i in range(days_in_calendar):
            final_date = next_monday + timedelta(days = i - 1)
            meeting = CalendarSupervisor.objects.filter(date = final_date, owner = request.user.employee)
            next_week[final_date] = meeting
        
        team = Employee.objects.filter(supervisor = request.user.employee)
        return render(request, 'manager_app/dashboard.html', {
            'last_week': last_week,
            'this_week': this_week,
            'next_week': next_week,
            'team': team
        })


class EmployeeView(LoginRequiredMixin, View):
    """class fer Emlpoyers list Viev

    Args:
        none

    Returns:
        team [QuerySet]: Objects of Employee model with 'supervisor' set on current user
    """
    
    def get(self, request):
        user = User.objects.get(id=request.user.id)
        user_employee = user.employee
        team = Employee.objects.filter(supervisor=user_employee)
        
        info = {}
        for employee in team:
            info['employee'] = employee
            
            
        
        return render(request, 'manager_app/employees.html', {'team': team})


class EmployeeCreateView(LoginRequiredMixin, PermissionRequiredMixin, View):
    """View fo creating new users.
    Creates new user and new Emploee
        
    Returns: 
        
    """
    permission_required = 'auth.add_user'
    
    def get(self, request):
        form = EmployeeAddForm()
        return render(request, 'manager_app/employee_form.html', {'form': form, 'legend': 'Dodaj nowego pracownika'})
    
    def post(self, request):
        form = EmployeeAddForm(request.POST)
        if form.is_valid():
            new_user = User.objects.create_user(
                username=form.cleaned_data['username'],
                password=form.cleaned_data['password1'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                is_staff=False,
                is_active=True,
            )
            new_employee = Employee.objects.create(
                phone=form.cleaned_data['phone'],
                role=form.cleaned_data['role'],
                supervisor=form.cleaned_data['supervisor'],
                user=new_user
            )
            return redirect(f'/employees/{new_employee.id}/')
        else:
            return render(request, 'manager_app/employee_form.html', {'form': form, 'legend': 'Dodaj nowego pracownika'})


class EmployeeDetailsView(LoginRequiredMixin, View):
    """ 
    Details Viev for Employee model  objects

    Args:
        
        id_ (int): id of object in Emploee model
    Returns:
        employee [object]: Emloyee object
    """
    def get(self, request, id_):
        employee = Employee.objects.get(id=id_)
        return render(request, 'manager_app/employee_details.html', {'employee': employee})


class EmployeeEditView(LoginRequiredMixin, View):
    """
    View for modify Empployee models

    Args:
        id_ (int): id of emloyee object
    
    Returns:
        form : with curent values
        legend (str): legend for form
    """
    def get(self, request, id_):
        employee = Employee.objects.get(id=id_)
        form = EmployeeEditForm(initial={
            'first_name': employee.user.first_name,
            'last_name': employee.user.last_name,
            'email': employee.user.email,
            'phone': employee.phone,
            'role': employee.role,
            'supervisor': employee.supervisor
        })
        
        return render(request, 'manager_app/employee_form.html', {'form': form, 'legend': 'Edycja Pracownika'})
    
    def post(self, request, id_):
        form = EmployeeAddForm(request.POST)
        if form.is_valid():
            edited_user = Employee.objects.get(id=id_).user
            User.objects.update(
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
            )
            edited_employee = Employee.objects.create(
                phone=form.cleaned_data['phone'],
                role=form.cleaned_data['role'],
                supervisor=form.cleaned_data['supervisor'],
                user=edited_user
            )
            return redirect(f'/employee/{edited_employee.id}/')
        else:
            return render(request, 'manager_app/employee_form.html', {'form': form, 'legend': 'Dodaj nowego pracownika'})
        

class ClientCreateView(LoginRequiredMixin, View):
    """
    Viev for create Client
    redirect to Create Branch
    """
    def get(self, request):
        form = ClientForm()
        return render(
            request, 
            'manager_app/client_form.html', 
            {'form': form, 'legend': 'Tworzenie nowego klienta'}
        )
        
    def post(self, request):
        form = ClientForm(request.POST, request.FILES)
        if form.is_valid():
            new_client = Client()
            new_client.company_name = form.cleaned_data['company_name']
            new_client.nip = form.cleaned_data['nip']
            new_client.logo = form.cleaned_data['logo']
            new_client.regon = form.cleaned_data['regon']
            new_client.krs = form.cleaned_data['krs']
            new_client.type = form.cleaned_data['type']
            new_client.save()
            return redirect(f'/branch/add/')
        else:
            return render(
            request, 
            'manager_app/client_form.html', 
            {
                'form': form, 
                'legend': 'Tworzenie nowego klienta', 
                'answer': 'Wystąpił błąd. Spróbuj ponownie'
            }
        )


class ClientDetailsView(LoginRequiredMixin, View):
    """
    View for details of client and branch
    """
    def get(self, request, id_):
        client = Client.objects.get(id=id_)
        return render(request, 'manager_app/client_details.html', {'client': client})


class ClientListView(LoginRequiredMixin, View):
    def get(self, request):
        traders = Employee.objects.filter(supervisor=request.user.employee)
        return render(request, 'manager_app/clients.html', {'traders': traders})
    
    
class ClientUpdateView(LoginRequiredMixin, UpdateView):
    """
    View for update Client
    """
    model = Client
    fields = '__all__'
    success_url = f'/clients/'
    
    
class BranchCreateView(LoginRequiredMixin, CreateView):
    """
    View for create Branch
    """
    model = Branch
    fields = '__all__'
    success_url = '/clients/'


class BranchUpdateView(LoginRequiredMixin, UpdateView):
    """
    View  for update Branch
    """
    model = Branch
    fields = '__all__'
    success_url = '/clients/'
    
    
class ProductCreateView(LoginRequiredMixin, CreateView):
    """
    View for create Product
    """
    model = Product
    fields = '__all__'
    success_url = '/variant/add/'


class ProductUpdateView(LoginRequiredMixin, UpdateView):
    """
    View  for update Branch
    """
    model = Product
    fields = '__all__'
    succes_url = '/products/'

class ProductListView(LoginRequiredMixin, View):
    """
    View for list of Products and Variants
    """
    def get(self, request):
        products = Product.objects.filter(is_active=True)
        list = {}
        for product in products:
            list[product.name] = Variant.objects.filter(product_id=product, is_active=True)
        return render(request, 'manager_app/products.html', {'products': list})


class VariantCreateView(LoginRequiredMixin, View):
    """
    View for add new variants to product
    """
    def get(self, request):
        form = VariantForm()
        return render(request, 'manager_app/variant_form.html', {'form': form, 'legend': 'Dodaj nowy wariant produktu'})
    
    def post(self, request):
        form = VariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = Variant()
            variant.dose = form.cleaned_data['dose']
            variant.unit = form.cleaned_data['unit']
            variant.in_package = form.cleaned_data['in_package']
            variant.photo_main = form.cleaned_data['photo_main']
            variant.photo_2 = form.cleaned_data['photo2']
            variant.photo_3 = form.cleaned_data['photo3']
            variant.photo_4 = form.cleaned_data['photo4']
            variant.photo_5 = form.cleaned_data['photo5']
            variant.photo_6 = form.cleaned_data['photo6']
            variant.photo_7 = form.cleaned_data['photo7']
            variant.photo_8 = form.cleaned_data['photo8']
            variant.photo_9 = form.cleaned_data['photo9']
            variant.photo_10 = form.cleaned_data['photo10']
            variant.product_id = form.cleaned_data['product']
            variant.next_delivery = form.cleaned_data['next_delivery']
            variant.save()
            return redirect('/products/')
        else:
            return render(request, 'manager_app/variant_form.html', {'form': form, 'legend': 'Dodaj nowy wariant produktu'})


class VariantUpdateView(LoginRequiredMixin, View):
    """
    View for update variants
    """
    def get(self, request, id_):
        variant = Variant.objects.get(id=id_)
        form = VariantForm(initial={
            'product': variant.product_id,
            'dose': variant.dose,
            'unit': variant.unit,
            'in_package': variant.in_package,
            'next_delivery': variant.next_delivery,
            'photo_main': variant.photo_main,
            'photo2': variant.photo_2,
            'photo3': variant.photo_3,
            'photo4': variant.photo_4,
            'photo5': variant.photo_5,
            'photo6': variant.photo_6,
            'photo7': variant.photo_7,
            'photo8': variant.photo_8,
            'photo9': variant.photo_9,
            'photo10': variant.photo_10
        })
        return render(request, 'manager_app/variant_form.html', {'form': form, 'legend': 'Edytuj wariant produktu'})
    
    def post(self, request):
        form = VariantForm(request.POST, request.FILES)
        if form.is_valid():
            variant = Variant()
            variant.dose = form.cleaned_data['dose']
            variant.unit = form.cleaned_data['unit']
            variant.in_package = form.cleaned_data['in_package']
            variant.photo_main = form.cleaned_data['photo_main']
            variant.photo_2 = form.cleaned_data['photo2']
            variant.photo_3 = form.cleaned_data['photo3']
            variant.photo_4 = form.cleaned_data['photo4']
            variant.photo_5 = form.cleaned_data['photo5']
            variant.photo_6 = form.cleaned_data['photo6']
            variant.photo_7 = form.cleaned_data['photo7']
            variant.photo_8 = form.cleaned_data['photo8']
            variant.photo_9 = form.cleaned_data['photo9']
            variant.photo_10 = form.cleaned_data['photo10']
            variant.product_id = form.cleaned_data['product']
            variant.next_delivery = form.cleaned_data['next_delivery']
            variant.save()
            return redirect('/products/')
        else:
            return render(request, 'manager_app/variant_form.html', {'form': form, 'legend': 'Dodaj nowy wariant produktu'})
        

class BatchCreateView(LoginRequiredMixin, CreateView):
    """
    View for create Batch
    """
    model = Batch
    fields = '__all__'
    success_url = '/products/'


class OrderCartCreateView(LoginRequiredMixin, View):
    """
    View for new Order and Cart
    """
    def get(self, request, branch_id):
        branch = Branch.objects.get(id=branch_id)
        form = CartForm()
        return render(request, 'manager_app/cart_form.html', {'title': f'Nowe zamówienie dla {branch}', 'form': form})

    def post(self, request, branch_id):
        form = CartForm(request.POST)
        branch = Branch.objects.get(id = branch_id)
            
        if form.is_valid():
            # create order
            today = date.today()
            order_number = '{}/{}/{}/{}'.format(
                branch.id,
                today.year,
                today.month,
                len(Order.objects.filter(branch=branch, date__year__gte=int(today.year), date__month__gte=int(today.month)))+1
            )
            order = Order.objects.create(
                order_number=order_number,
                branch=branch,
            )
            
            # Create cart
            cart = Cart()
            cart.order = order
            cart.quantity = int(form.cleaned_data['quantity'])
            
            variant = form.cleaned_data.get('variant')
            batch = variant.batch_set.filter(is_active=True)[0]
            for element in variant.batch_set.filter(is_active=True):
                if element.quantity < batch.quantity and element.quantity > int(form.cleaned_data['quantity']):
                    batch  = element
            cart.batch = batch
            cart.save()
            
            return redirect(f'/branch/{branch.id}/orders/{order.id}/')
        else:
            return render(request, 'manager_app/cart_form.html', {'title': f'Nowe zamówienie dla {branch}', 'form': form})


class CartModifyView(LoginRequiredMixin, View):
    """
    View for adding posiotions to Cart
    """
    def get(self, request, branch_id, order_id):
        branch = Branch.objects.get(id=branch_id)
        order = Order.objects.get(id=order_id)
        
        positions = Cart.objects.filter(order=order).order_by('id')
        form = CartForm()
        return render(request, 'manager_app/cart_form.html', {
            'title': f'Zamówienie dla {branch}', 
            'form': form,
            'positions': positions,
            'order': order
        })
        
    def post(self, request, branch_id, order_id):
        form = CartForm(request.POST)
        order = Order.objects.get(id=order_id)
        if form.is_valid():
            new_cart = Cart()
            new_cart.order = order
            new_cart.quantity = int(form.cleaned_data['quantity'])
            variant = form.cleaned_data.get('variant')
            batch = variant.batch_set.filter(is_active=True)[0]
            for element in variant.batch_set.filter(is_active=True):
                if element.quantity < batch.quantity and element.quantity > int(form.cleaned_data['quantity']):
                    batch  = element
            new_cart.batch = batch
            new_cart.save()
        
        branch = Branch.objects.get(id=branch_id)
        positions = Cart.objects.filter(order=order).order_by('id')
        return render(request, 'manager_app/cart_form.html', {
            'title': f'Zamówienie dla {branch}', 
            'form': form,
            'positions': positions,
            'order': order
        })
        
        
class CartDeleteView(LoginRequiredMixin, View):
    """
    View remove positiom from Cart
    """
    def get(self, request, branch_id, order_id, position_id):
        position = Cart.objects.get(id=position_id)
        position.delete()
        
        return redirect(f'/branch/{branch_id}/orders/{order_id}/')


class OrderStatusUpdateView(LoginRequiredMixin, View):
    def get(self, request, branch_id, order_id, status_value):
        order = Order.objects.get(id=order_id)
        order.order_status = status_value
        order.save()
        if status_value == 0:
            return redirect(f'/branch/{branch_id}/orders/{order_id}/')
        else:
            return redirect('/orders/')


class OrderDeleteView(LoginRequiredMixin, View):
    """
    View for delete Order
    """
    def get(self, request, order_id):
        order = Order.objects.get(id=order_id)
        order.delete()
        
        return redirect(f'/orders/')


class OrderListView(LoginRequiredMixin,View):
    """
    Lists of all Orders without ended
    """
    def get(self, request):
        orders = Order.objects.filter(order_status__in=[0, 1, 2, 3, 4, 5, 6]).order_by('order_status', '-date')
        
        result = {}
        for status in ORDER_STATUS:
            st_orders = orders.filter(order_status = status[0])
            result[status[1]] = st_orders
        return render(request, 'manager_app/orders.html', {'orders': result})
    
class OrderCSModifyView(LoginRequiredMixin, UpdateView):
    """
    View for Customer Service to manage order manualy
    """
    model = Order
    fields = ['order_number', 'branch', 'invoice', 'discount']
    success_url = '/orders/'

